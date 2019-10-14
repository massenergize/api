# Carbon Calculator API
# Brad Hubbard-Nelson (bradhn@mindspring.com)
#
#imports
from datetime import date,datetime
from .models import Action,Question,Event,Station,Group,ActionPoints,CarbonCalculatorMedia
from django.utils import timezone
from .homeHeating import HeatingLoad
from database.utils.create_factory import CreateFactory
from database.utils.database_reader import DatabaseReader
import jsons
import json
import csv
from django.core import files
from io import BytesIO
import requests

# constants
YES = "Yes"
NO = "No"
FRACTIONS = ["None","Some","Half","Most","All"]
DATE = str(date.today())
NUM = 0   
VALID_QUERY = 0
INVALID_QUERY = -1
HEATING_SYSTEM_POINTS = 10000
SOLAR_POINTS = 6000
ELECTRICITY_POINTS = 5000

def SavePic2Media(picURL):
    if picURL == '':
        return None
    # in the import from AirTable, picture files have the url between ( ) after the original picture name
    loc1 = picURL.find('(')
    loc2 = picURL.find(')')
    if loc1>0 and loc2>0:
        picURL = picURL[loc1+1:loc2]
    print("Importing picture from: "+picURL)
    try:
        resp = requests.get(picURL)
        if resp.status_code != requests.codes.ok:
            # Error handling here3
            print("ERROR: Unable to import action photo from "+picURL)
            return None
        else:
            file_name = picURL.split("/")[-1]  # There's probably a better way of doing this but this is just a quick example
            fp = open(file_name,"wb")
            fp.write(resp.content)
            fp.close()
            media=CarbonCalculatorMedia(file = file_name)
            if media:
                media.save()
                return media
            else:
                return None
    except:
        print("Error encountered")
        return None

class CarbonCalculator:

    def __init__(self) :
        self.allActions = {  
                        'energy_fair':EnergyFair,
                        'energy_audit':EnergyAudit,
                        'prog_thermostats':ProgrammableThermostats,
                        'weatherization':Weatherize,
                        'community_solar':CommunitySolar,
                        'renewable_elec':RenewableElectricity,
                        'led_lighting':LEDLighting,
                        'heating_assessment':HeatingAssessment,
                        'efficient_fossil':EfficientBoilerFurnace,
                        'air_source_hp':AirSourceHeatPump,
                        'ground_source_hp':GroundSourceHeatPump,
                        'hw_assessment':HotWaterAssessment,
                        'hp_water_heater':HeatPumpWaterHeater,
                        'solar_assessment':SolarAssessment,
                        'install_solarHW':InstallSolarPV,
                        'install_solarPV':InstallSolarHW,
                        'energystar_fridge':EnergystarRefrigerator,
                        'energystar_washer':EnergystarWasher,
                        'induction_stove':InductionStove,
                        'hp_dryer':HeatPumpDryer,
                        'coldwater_wash':ColdWaterWash,
                        'line_dry':LineDry,
                        #'unplug_appliances':UnusedAppliances,
                        'fridge_pickup':RefrigeratorPickup,
                        'smart_power_strip':SmartPowerStrip,
                        'electricity_monitor':ElectricityMonitor,
                        'replace_car':ReplaceCar,
                        'reduce_car_miles':ReduceMilesDriven,
                        #'replace_car2':ReplaceCar2,
                        #'reduce_car2_miles':ReduceMilesDriven2,
                        'eliminate_car':EliminateCar,
                        'reduce_flights':ReduceFlights,
                        'offset_flights':OffsetFlights,
                        'low_carbon_diet':LowCarbonDiet,
                        'reduce_waste':ReduceWaste,
                        'compost':Compost,
                        #'lawn_assessment':LawnAssessment,
                        'reduce_lawn_size':ReduceLawnSize,
                        'reduce_lawn_care':ReduceLawnCare,
                        'electric_mower':ElectricMower,
                        'rake_elec_blower':RakeOrElecBlower,
                        }
        for name in self.allActions.keys():
            theClass = self.allActions[name]
            theInstance = theClass(name)
            self.allActions[name] = theInstance
        
    def Query(self,action=None):
        if action in self.allActions:
            return self.allActions[action].Query()
        else:
            return self.AllActionsList()

    def AllActionsList(self):
        response = {}
        actionList = []
        for action in self.allActions:
            name = self.allActions[action].name
            description = self.allActions[action].description
            actionList.append( {'name':name, 'description':description} )
        response['actions'] = actionList
        response['status'] = VALID_QUERY
        return response

    def QueryEvents(self,event=None):
        if event:
            qs = Event.objects.filter(name=event)
            if qs:
                q = qs[0]
                host_logo_url = sponsor_logo_url = ""
                if q.host_logo:
                    print(q.host_logo)
                    if q.host_logo.pk:
                    # locate Media, get file and get the URL
                        pass
                return {"status":True,"EventInfo":{"name":q.name, "displayname":q.displayname, "datetime":q.datetime, "location":q.location,"stations":q.stationslist,
                                "host_org":q.host_org, "host_contact":q.host_contact, "host_email":q.host_email, "host_phone":q.host_phone,"host_url":q.host_url,"host_logo":host_logo_url,
                                "sponsor_org":q.sponsor_org, "sponsor_url":q.sponsor_url,"sponsor_logo":sponsor_logo_url}}
            else:
                return {"status":False, "statusText":"Event ("+event+") not found"}
        else:
            qs = Event.objects.all()
            if qs:

                eventInfo = []
                for q in qs:
                    info = {"name":q.name, "displayname":q.displayname, "datetime":q.datetime, "location":q.location}
                    eventInfo.append(info)
                return {"status":True,"eventList":eventInfo}
            else:
                return {"status":False,"statusText":"No events found"}

    def QueryStations(self,station=None):
        if station:
            qs = Station.objects.filter(name=station)
            if qs:
                q = qs[0]
                return {"status":True,"StationInfo":{"name":q.name, "displayname":q.displayname, "description":q.description, "actions":q.actions}}
            else:
                return {"status":False, "statusText":"Station ("+station+") not found"}
        else:
            qs = Station.objects.all()
            if qs:

                stationInfo = []
                for q in qs:
                    info = {"name":q.name, "displayname":q.displayname}
                    stationInfo.append(info)
                return {"status":True,"stationList":stationInfo}
            else:
                return {"status":False,"statusText":"No stations found"}


    def Estimate(self, action, inputs, save=False):
# inputs is a dictionary of input parameters
# outputs is a dictionary of results
        status = INVALID_QUERY
        if action in self.allActions:
            # community context
            #community = inputs.get("community", "unknown")

            theAction = self.allActions[action]
            #if theAction.Eval(inputs) == VALID_QUERY:
            #    points = theAction.points
            #    cost = theAction.cost
            #    savings = theAction.savings
            #status = VALID_QUERY
            results = theAction.Eval(inputs)
            if save:
                results = self.RecordActionPoints(action,inputs,results)
            return results
        else:    
            outputs = {}
            outputs["status"] = status
        #outputs["carbon_points"] = points
        #outputs["action_cost"] = cost
        #outputs["annual_savings"] = savings
            return outputs

    def RecordActionPoints(self,action, inputs,results):
        user_id = inputs.pop("MEId",None)
            
        record = ActionPoints(  user_id=user_id,
                                action=action,
                                choices=inputs,
                                points=results.get("carbon_points",0),
                                cost= results.get("cost",0),
                                savings = results.get("savings",0))
        record.save()
        return results

    def Reset(self,inputs):
        if inputs.get('Confirm',NO) == YES:
            print(Action.objects.all().delete())
            print(Question.objects.all().delete())
            print(Event.objects.all().delete())
            print(Station.objects.all().delete())
            print("Deleted Actions, Questions, Events and Stations")
            return {"status":True}
        else:
            return {"status":False}

    def Import(self,inputs):
        if inputs.get('Confirm',NO) == YES:
            status = False
            actionsFile = inputs.get('Actions','')
            if actionsFile!='':
                with open(actionsFile, newline='') as csvfile:
                    inputlist = csv.reader(csvfile)
                    first = True
                    for item in inputlist:
                        if first:
                            #header = item
                            first = False
                        else:
                            if item[0] == '':
                                continue

                            qs = Action.objects.filter(name=item[0])
                            if qs:
                                qs[0].delete()

                            #if action[5]!='':
                            #    import this media filt
                            #    actionPicture = Media()
                            picture = None
                            if len(item)>=4 and item[0]!='':
                                picture = SavePic2Media(item[5])

                                action = Action(name=item[0],
                                    description=item[1],
                                    helptext=item[2],
                                    average_points=int(eval(item[3])),
                                    questions=item[4].split(","),
                                    picture = picture)
                                print('Importing Action ',action.name,': ',action.description)
                                action.save()

                    status = True

            questionsFile = inputs.get('Questions','') 
            if questionsFile!='':
                with open(questionsFile, newline='') as csvfile:
                    inputlist = csv.reader(csvfile)
                    first = True
                    for item in inputlist:
                        if first:
                            #header = item
                            first = False
                        else:
                            if item[0] == '':
                                continue

                            qs = Question.objects.filter(name=item[0])
                            if qs:
                                qs[0].delete()

                             #if action[5]!='':
                            #    import this media filt
                            #    actionPicture = Media()
                            skip = [[],[],[],[],[],[]]
                            for i in range(6):
                                ii = 5+2*i
                                if item[ii]!='' :
                                    skip[i] = item[ii].split(",") 
                            question = Question(name=item[0],
                                category=item[1],
                                question_text=item[2],
                                question_type=item[3],
                                response_1=item[4], skip_1=skip[0],
                                response_2=item[6], skip_2=skip[1],
                                response_3=item[8], skip_3=skip[2],
                                response_4=item[10], skip_4=skip[3],
                                response_5=item[12], skip_5=skip[4],
                                response_6=item[14], skip_6=skip[5])
                                
                            print('Importing Question ',question.name,': ',question.question_text)
                            question.save()
                    status = True

            stationsFile = inputs.get('Stations','') 
            if stationsFile!='':
                with open(stationsFile, newline='') as csvfile:
                    inputlist = csv.reader(csvfile)
                    first = True
                    for item in inputlist:
                        if first:
                            #header = item
                            first = False
                        else:
                            if item[0] == '':
                                continue

                            qs = Station.objects.filter(name=item[0])
                            if qs:
                                qs[0].delete()

                            station_icon = SavePic2Media(item[3])

                            station = Station(name=item[0],
                                displayname=item[1],
                                description=item[2],
                                icon = station_icon,
                                actions=item[5].split(","))
                                
                            print('Importing Station ',station.name,': ',station.description)
                            station.save()
                    status = True
            
            eventsFile = inputs.get('Events','') 
            if eventsFile!='':
                with open(eventsFile, newline='') as csvfile:
                    inputlist = csv.reader(csvfile)
                    first = True
                    for item in inputlist:
                        if first:
                            #header = item
                            first = False
                        else:
                            if item[0] == '':
                                continue
                            qs = Event.objects.filter(name=item[0])
                            if qs:
                                qs[0].delete()

                            host_logo = None
                            sponsor_logo = None
                            eventdate = item[2]
                            if eventdate != '':
                                dt = datetime.strptime(item[2].upper(), '%m/%d/%Y %H:%M%p')
                                current_tz = timezone.get_current_timezone()
                                dt = current_tz.localize(dt)
                            else:
                                dt= ''
                            host_logo = SavePic2Media(item[11])
                            sponsor_logo = SavePic2Media(item[14])
                            groupslist = None
                            if item[5]!='':
                                groupslist = item[5].split(",")

                            event = Event(name=item[0],
                                displayname=item[1],
                                datetime = dt,
                                location = item[3],
                                stationslist = item[4].split(","),
                                host_org = item[6],
                                host_contact = item[7],
                                host_email = item[8],
                                host_phone = item[9],
                                host_url = item[10],
                                host_logo = host_logo,
                                sponsor_org = item[12],
                                sponsor_url = item[13],
                                sponsor_logo = sponsor_logo
                                )
                            event.save()
                            if groupslist:
                                for group in groupslist:
                                    g = Group.objects.filter(name=group)
                                    if g:
                                        gg = g[0]
                                        event.groups.add(gg)
                            print('Importing Event ',event.name,' at ',event.location,' on ',event.datetime)
                            event.save()
                    status = True
            groupsFile = inputs.get('Groups','') 
            if groupsFile!='':
                with open(groupsFile, newline='') as csvfile:
                    inputlist = csv.reader(csvfile)
                    first = True
                    for item in inputlist:
                        if first:
                            #header = item
                            first = False
                        else:
                            if item[0] == '':
                                continue
                            qs = Group.objects.filter(name=item[0])
                            if qs:
                                qs[0].delete()

                            #if action[5]!='':
                            #    import this media filt
                            #    actionPicture = Media()
                            group = Group(name=item[0],
                                displayname=item[1],
                                description = item[2],
                                members = item[3],
                                points = item[4],
                                savings = item[5]
                                )
                                
                            print('Importing Group ',group.displayname)
                            group.save()
                    status = True
            self.__init__()    
            return {"status":status}
        else:
            return {"status":False}


class CalculatorQuestion:
    def __init__(self, name):
        self.name = name

        qs = Question.objects.filter(name=name)
        if qs:
            q = qs[0]
            self.category = q.category
            self.questionText = q.question_text
            self.questionType = q.question_type
            self.responses = []
            if q.question_type == 'Choice':
                if q.response_1 != '':
                    response = {'text':q.response_1}
                    if len(q.skip_1)>0:
                        response['skip']=q.skip_1
                    self.responses.append(response)
                if q.response_2 != '':
                    response = {'text':q.response_2}
                    if len(q.skip_2)>0:
                        response['skip']=q.skip_2
                    self.responses.append(response)
                if q.response_3 != '':
                    response = {'text':q.response_3}
                    if len(q.skip_3)>0:
                        response['skip']=q.skip_3
                    self.responses.append(response)
                if q.response_4 != '':
                    response = {'text':q.response_4}
                    if len(q.skip_4)>0:
                        response['skip']=q.skip_4
                    self.responses.append(response)
                if q.response_5 != '':
                    response = {'text':q.response_5}
                    if len(q.skip_5)>0:
                        response['skip']=q.skip_5
                    self.responses.append(response)
                if q.response_6 != '':
                    response = {'text':q.response_6}
                    if len(q.skip_6)>0:
                        response['skip']=q.skip_6
                    self.responses.append(response)
        else:
            print("ERROR: Question "+name+" was not found")


class CalculatorAction:
    def __init__(self,name):       
        self.name = name
        self.description = "Action short description"
        self.helptext = "This text explains what the action is about, in 20 words or less."
        self.questions = []    # question with list of valid responses.
        self.average_points = 0
        self.points = 0
        self.cost = 0
        self.savings = 0
#
#    def load(self,name):
        qs = Action.objects.filter(name=name)
        try: #if len(qs)>0:
            q = qs[0]
            self.description=q.description
            self.helptext = q.helptext

            for question in q.questions:
                qq = CalculatorQuestion(question)
                #print(jsons.dump(CalculatorQuestion(question)))
                self.questions.append(jsons.dump(qq))
            self.average_points = q.average_points
            self.initialized = True
        except:
            print("ERROR: Action "+name+" was not found")
            self.initialized = False

    def Query(self):
        return {'status':VALID_QUERY, 'name':self.name, 'description':self.description, 'average_carbon_points':self.average_points, 'helptext':self.helptext, 'questions':jsons.dump(self.questions)}

    def Eval(self, inputs):
        return {'status':VALID_QUERY, 'carbon_points':self.points, 'cost':self.cost, 'savings':self.savings}

ENERGY_FAIR_POINTS = 50
class EnergyFair(CalculatorAction):
        # inputs:   MEid (MassEnergize profile ID) if available.  If not no record keeping
        # attend_fair,own_rent,fuel_assistance,activity_group
    def Eval(self, inputs):
        if not self.initialized:
            return {'status':INVALID_QUERY}            
        self.points = 0
        if inputs.get('attend_fair',NO) == YES:
            # a trivial bonus points action
            self.points = ENERGY_FAIR_POINTS
            # TODO: save action to ME profile

        return super().Eval(inputs)

ENERGY_AUDIT_POINTS = 250
ELEC_UTILITY = 'elec_utility'
class EnergyAudit(CalculatorAction):
    def Eval(self, inputs):
        # inputs: MEid (MassEnergize user)
        #         community
        #         signup_energy_audit  YesNo
        #         last_audit_year  (year number)
        #         already_had_audit YesNo
        #energy_audit_recently,energy_audit,heating_system_fuel,electric_utility
        signup_energy_audit = inputs.get(self.name, YES)
        already_had_audit = inputs.get("energy_audit_recently", YES) # get default from db if user entered
        if signup_energy_audit == YES and already_had_audit != YES:

            # permissible to sign up for audit
            self.points = ENERGY_AUDIT_POINTS
        return super().Eval(inputs)

HEATING_FUEL = "Heating Fuel"
FUELS = ["Fuel Oil","Natural Gas","Propane","Electric Resistance","Electric Heat Pump","Wood","Other"]
HAVE_PSTATS = "have_prog_thermostats"
PSTAT_PROGRAMMING = "prog_thermostat_programming"
class ProgrammableThermostats(CalculatorAction):
    def Eval(self, inputs):
        #have_pstats,pstats_programmed,install_programmable_thermostats,heating_system_fuel

        install_pstats = inputs.get(self.name,YES)
        have_pstats = inputs.get(HAVE_PSTATS,NO)
        heating_fuel = inputs.get(HEATING_FUEL,FUELS[0])
        if install_pstats == YES and have_pstats == NO :
            # need to know total fuel consumption
            heatingCO2, heatingCost = HeatingLoad(heating_fuel)     # to gross approximation
            pstat_load_reduction = 0.15
            self.points = pstat_load_reduction * heatingCO2
            self.savings = pstat_load_reduction * heatingCost
            self.cost = 150. 
        return super().Eval(inputs)

HOME_WEATHERIZED = "home_weatherized"
class Weatherize(CalculatorAction):
    def Eval(self, inputs):
        #weatherized,insulate_home,heating_system_fuel

        weatherize_home = inputs.get(self.name,YES)
        # could get this from fuel usage ...
        home_weatherized = inputs.get(HOME_WEATHERIZED,YES)
        heating_fuel = inputs.get(HEATING_FUEL,FUELS[0])
        if weatherize_home == YES and home_weatherized != YES:
            # need to know total fuel consumption
            heatingCO2, heatingCost = HeatingLoad(heating_fuel)     # to gross approximation
            weatherize_load_reduction = 0.15
            self.points = weatherize_load_reduction * heatingCO2
            self.savings = weatherize_load_reduction * heatingCost
            self.cost = 500.     # figure out a typical value 
        return super().Eval(inputs)
 
MONTHLY_ELEC = "monthly_elec_bill",
class CommunitySolar(CalculatorAction):
    def Eval(self, inputs):
        #community_solar,monthly_elec,electric_utility

        join_community_solar = inputs.get(self.name,YES)
        monthly_elec_bill = inputs.get(MONTHLY_ELEC, 150.)
        fractional_savings = 0.1       # "save 10% of electric bill"
        if join_community_solar == YES:
            self.points = 0.
            self.savings = fractional_savings * 12. * monthly_elec_bill
            self.cost = 1000.    # figure out a typical value
        return super().Eval(inputs)

RENEWABLE_FRACTION = "renewable_elec_fraction"
class RenewableElectricity(CalculatorAction):
    #choose_renewable,monthly_elec,electric_utility
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

LED_SWAP_FRACTION = "fraction_led_replacement"
NUM_OLD_BULBS = "number_nonefficient_bulbs"
class LEDLighting(CalculatorAction):
    #bulbs_incandescent,bulbs_replace_leds
    def Eval(self, inputs):
        num_old_bulbs = inputs.get(NUM_OLD_BULBS ,10)
        replace_fraction = inputs.get("numeric_fraction_led_replacement",0.)
        replace_fraction1 = inputs.get(LED_SWAP_FRACTION,FRACTIONS[0])
        # if they can get energy audit it's free
        bulb_price = 0.
        if replace_fraction == 0. and replace_fraction1 != "None":
            if replace_fraction1 == "All":
                replace_fraction = 1.
            elif replace_fraction1 == "Most":
                replace_fraction = 0.75
            elif replace_fraction1 == "Half":
                replace_fraction = 0.5
            elif replace_fraction1 == "Some":
                replace_fraction = 0.25

        average_watts = 60
        average_ontime = 3
        average_kwh = average_watts * average_ontime * 365 / 1000
        saved_kwh = (1 - 0.12) * replace_fraction * num_old_bulbs * average_kwh
        elec_co2_kwh = .75
        elec_price_kwh = .2
        if num_old_bulbs > 0 and replace_fraction>0.:
            self.points = saved_kwh * elec_co2_kwh
            self.savings = saved_kwh * elec_price_kwh
            self.cost = bulb_price * replace_fraction * num_old_bulbs
        return super().Eval(inputs)

HEATING_SYSTEM = "heating_system_type"
HEATING_AGE = "heating_system_age"
AC_TYPE = "AC_type"
AC_AGE = "AC_age"
AGE_OPTIONS = ["<10 years","10-20 years",">20 years"]
HEATING_SYSTEMS = ["Boiler","Furnace","Baseboard","Wood Stove","Other"]
AC_TYPES = ["None","Central","Wall","Other"]
class HeatingAssessment(CalculatorAction):
    #heating_system_assessment,heating_system_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    def Eval(self, inputs):
        self.points = self.average_points        
        return super().Eval(inputs)

HEATING_EFF = 'heating_efficiency'
NEW_SYSTEM = 'new_system'
class EfficientBoilerFurnace(CalculatorAction):
    #upgrade_heating_system_efficiency,heating_system_fuel,heating_system_type,heating_system_age

    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class AirSourceHeatPump(CalculatorAction):
    #upgrade_heating_with_ashp,heating_system_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class GroundSourceHeatPump(CalculatorAction):
    #install_gshp,heating_system_fuel,heating_system_type,heating_system_age,air_conditioning_type,air_conditioning_age
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class HotWaterAssessment(CalculatorAction):
    #hot_water_assessment,water_heater_type,water_heater_age
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class HeatPumpWaterHeater(CalculatorAction):
    #replace_water_heater,water_heater_type,water_heater_age
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

SOLAR_POTENTIAL = 'solar_potential'
POTENTIALS = ['Not sure','Poor', 'Good', 'Great']
class SolarAssessment(CalculatorAction):
    #solar_assessment,solar_potential
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

ARRAY_SIZE = 'solar_pv_size'
class InstallSolarPV(CalculatorAction):
    #install_solar_panels,solar_potential
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class InstallSolarHW(CalculatorAction):
    #install_solar_hw,solar_potential
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class EnergystarRefrigerator(CalculatorAction):
    #replace_refrigerator,refrigerator_age
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class EnergystarWasher(CalculatorAction):
    #replace_washer,washer_age,wash_loads
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class InductionStove(CalculatorAction):
    #induction_stove,stove_type
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class HeatPumpDryer(CalculatorAction):
    #replace_dryer,dryer_type
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class ColdWaterWash(CalculatorAction):
    #cold_water_wash,wash_loads
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class LineDry(CalculatorAction):
    #line_or_rack_dry_loads,wash_loads
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

#class UnusedAppliances(CalculatorAction):
#    def Eval(self, inputs):
#        return super().Eval(inputs)

class RefrigeratorPickup(CalculatorAction):
    #extra_refrigerator,extra_refrigerator_age,extra_refrigerator_pickup,unplug_refrigerator
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class SmartPowerStrip(CalculatorAction):
    #smart_power_strips
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class ElectricityMonitor(CalculatorAction):
    #install_electricity_monitor
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

CAR_POINTS = 8000
class ReplaceCar(CalculatorAction):
    #transportation_car_type,replace_car,car_annual_miles,car_mpg,car_model_new
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class ReduceMilesDriven(CalculatorAction):
    #reduce_total_mileage,car_annual_miles,car_mpg,transportation_public,transportation_public_amount,transportation_commute_bike_walk,transportation_commute_bike_walk_amount,transportation_telecommute,transportation_telecommute_amount
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

#lass ReplaceCar2(CalculatorAction):
#   def Eval(self, inputs):
#       return super().Eval(inputs)
#
#class ReduceMilesDriven2(CalculatorAction):
#    def Eval(self, inputs):
#        return super().Eval(inputs)
#
class EliminateCar(CalculatorAction):
    #eliminate_car,transportation_car_type,car_annual_miles,car_mpg
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

FLIGHT_POINTS = 2000
class ReduceFlights(CalculatorAction):
    #flights_amount,transportation_flights
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class OffsetFlights(CalculatorAction):
    #flights_amount,offset_flights
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

DIET_POINTS = 1000
class LowCarbonDiet(CalculatorAction):
    #eating_switch_meals,family_size,meat_frequency,eating_switch_meals_amount
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class ReduceWaste(CalculatorAction):
    #reduce_waste,reuse_containers,buy_sell_used,buy_bulk,buy_recycled
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

COMPOST_POINTS = 100
class Compost(CalculatorAction):
    #compost_food_waste,compost_pickup
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

LAWN_ASSESSMENT_POINTS = 100
LAWN_SIZES = ["Small (up to 2000 sq ft)", "Medium (2000-4000 sq ft)","Large (4000-6000 sq ft)","Very large (above 6000 sq ft)"]
#class LawnAssessment(CalculatorAction):
#    def Eval(self, inputs):
#        return super().Eval(inputs)
#
class ReduceLawnSize(CalculatorAction):
    #lawn_size,reduce_lawn_size,mower_type,mowing_frequency
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class ReduceLawnCare(CalculatorAction):
    #lawn_size,lawn_service,mowing_frequency,mower_type,fertilizer,fertilizer_applications
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class ElectricMower(CalculatorAction):
    #lawn_size,mower_type,mower_switch
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)

class RakeOrElecBlower(CalculatorAction):
    #leaf_cleanup_gas_blower,leaf_cleanup_blower_switch
    def Eval(self, inputs):
        self.points = self.average_points
        return super().Eval(inputs)
