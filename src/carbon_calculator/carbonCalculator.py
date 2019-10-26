# Carbon Calculator API
# Brad Hubbard-Nelson (bradhn@mindspring.com)
#
#imports
from datetime import date,datetime
from .models import Action,Question,Event,Station,Group,ActionPoints,CarbonCalculatorMedia
from django.utils import timezone
from database.utils.create_factory import CreateFactory
from database.utils.database_reader import DatabaseReader
import json
import csv
from django.core import files
from io import BytesIO
import requests
from .CCConstants import YES,NO, VALID_QUERY, INVALID_QUERY
from .CCDefaults import getDefault, CCD
from .queries import QuerySingleAction, QueryAllActions
from .homeHeating import EvalEnergyAudit, EvalWeatherization, EvalProgrammableThermostats, EvalAirSourceHeatPump, \
                        EvalGroundSourceHeatPump, EvalHeatingSystemAssessment
from .electricity import EvalCommunitySolar, EvalRenewableElectricity, EvalLEDLighting, EvalEnergystarRefrigerator, \
                        EvalEnergystarWasher, EvalInductionStove, EvalHeatPumpDryer, EvalColdWaterWash, EvalLineDry, \
                        EvalRefrigeratorPickup, EvalSmartPowerStrip, EvalElectricityMonitor
from .solar import EvalSolarAssessment, EvalSolarPV
from .hotWater import EvalHotWaterAssessment, EvalHeatPumpWaterHeater, EvalSolarHW
from .transportation import EvalReplaceCar, EvalReduceMilesDriven, EvalEliminateCar, EvalReduceFlights, EvalOffsetFlights
from .foodWaste import EvalLowCarbonDiet, EvalReduceWaste, EvalCompost
from .landscaping import EvalReduceLawnSize, EvalReduceLawnCare, EvalRakeOrElecBlower, EvalElectricMower

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
    # query actions    
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

    def Estimate(self, action, inputs, save=False):
# inputs is a dictionary of input parameters
        queryFailed = {'status':INVALID_QUERY}
        if action in self.allActions:
            theAction = self.allActions[action]
            if not theAction.initialized:
                return queryFailed            

            results = theAction.Eval(inputs)
            if save:
                results = self.RecordActionPoints(action,inputs,results)
            return results
        else:    
            return queryFailed

    def RecordActionPoints(self,action, inputs,results):
        user_id = inputs.pop("UserID",None)            
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
                    csvfile.close()
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
                    csvfile.close()
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
                    csvfile.close()
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
                    csvfile.close()
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
                    csvfile.close()
                    status = True
            defaultsFile = inputs.get('Defaults','') 
            if defaultsFile!='':
                status = CCD.importDefaults(CCD,defaultsFile)

            self.__init__()    
            return {"status":status}
        else:
            return {"status":False}

    def Export(self,inputs):
        status = False
        defaultsFile = inputs.get('Defaults','')
        if defaultsFile!='':
            status = CCD.exportDefaults(CCD, defaultsFile)
        
        return {"status":status}

class CalculatorAction:
    def __init__(self,name):       
        self.name = name
        self.initialized = False
        self.description = "Action short description"
        self.helptext = "This text explains what the action is about, in 20 words or less."
        self.questions = []    # question with list of valid responses.
        self.average_points = 0
        self.points = 0
        self.cost = 0
        self.savings = 0
        self.text = "" # "Explanation for the calculated results."
        self.picture = ""
#
#    def load(self,name):
        status, actionInfo = QuerySingleAction(self.name)
        if status == VALID_QUERY:
            self.description = actionInfo["description"]
            self.helptext = actionInfo["helptext"]
            self.questions = actionInfo["questionInfo"]    # question with list of valid responses.
            self.average_points = actionInfo["average_points"]
            self.picture = actionInfo["picture"]
            self.initialized = True
            
    def Query(self):
        status, actionInfo = QuerySingleAction(self.name)
        return {"status":status, "action":actionInfo}

    def Eval(self, inputs):
        return {'status':VALID_QUERY, 'carbon_points':round(self.points,0), 'cost':round(self.cost,0), 'savings':round(self.savings,0), 'explanation':self.text}

ENERGY_FAIR_POINTS = 50
class EnergyFair(CalculatorAction):
    # a trivial bonus points action, part of registering for the energy fair
    # inputs: attend_fair,own_rent,fuel_assistance,activity_group
    def Eval(self, inputs):
        self.points = 0
        if inputs.get('attend_fair',NO) == YES:
            self.points = ENERGY_FAIR_POINTS
            self.text = "Thank you for participating!"
        return super().Eval(inputs)

class EnergyAudit(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalEnergyAudit(inputs)
        return super().Eval(inputs)

class ProgrammableThermostats(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalProgrammableThermostats(inputs)
        return super().Eval(inputs)

class Weatherize(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalWeatherization(inputs)
        return super().Eval(inputs)

class CommunitySolar(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalCommunitySolar(inputs)
        return super().Eval(inputs)

class RenewableElectricity(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalRenewableElectricity(inputs)
        return super().Eval(inputs)

class LEDLighting(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalLEDLighting(inputs)
        return super().Eval(inputs)

class HeatingAssessment(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalHeatingSystemAssessment(inputs)
        return super().Eval(inputs)

class EfficientBoilerFurnace(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalEfficientBoilerFurnace(inputs)
        return super().Eval(inputs)

class AirSourceHeatPump(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalAirSourceHeatPump(inputs)
        return super().Eval(inputs)

class GroundSourceHeatPump(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalGroundSourceHeatPump(inputs)
        return super().Eval(inputs)

class HotWaterAssessment(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalHotWaterAssessment(inputs)
        return super().Eval(inputs)

class HeatPumpWaterHeater(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalHeatPumpWaterHeater(inputs)
        return super().Eval(inputs)

class SolarAssessment(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalSolarAssessment(inputs)
        return super().Eval(inputs)

class InstallSolarPV(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalSolarPV(inputs)
        return super().Eval(inputs)

class InstallSolarHW(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalSolarHW(inputs)
        return super().Eval(inputs)

class EnergystarRefrigerator(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalEnergystarRefrigerator(inputs)
        return super().Eval(inputs)

class EnergystarWasher(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalEnergystarWasher(inputs)
        return super().Eval(inputs)

class InductionStove(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalInductionStove(inputs)
        return super().Eval(inputs)

class HeatPumpDryer(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalHeatPumpDryer(inputs)
        return super().Eval(inputs)

class ColdWaterWash(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalColdWaterWash(inputs)
        return super().Eval(inputs)

class LineDry(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalLineDry(inputs)
        return super().Eval(inputs)

class RefrigeratorPickup(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalRefrigeratorPickup(inputs)
        return super().Eval(inputs)

class SmartPowerStrip(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalSmartPowerStrip(inputs)
        return super().Eval(inputs)

class ElectricityMonitor(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalElectricityMonitor(inputs)
        return super().Eval(inputs)

CAR_POINTS = 8000
class ReplaceCar(CalculatorAction):
    #transportation_car_type,replace_car,car_annual_miles,car_mpg,car_model_new
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReplaceCar(inputs)
        return super().Eval(inputs)

class ReduceMilesDriven(CalculatorAction):
    #reduce_total_mileage,car_annual_miles,car_mpg,transportation_public,transportation_public_amount,transportation_commute_bike_walk,transportation_commute_bike_walk_amount,transportation_telecommute,transportation_telecommute_amount
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceMilesDriven(inputs)
        return super().Eval(inputs)

class EliminateCar(CalculatorAction):
    #eliminate_car,transportation_car_type,car_annual_miles,car_mpg
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalEliminateCar(inputs)
        return super().Eval(inputs)

FLIGHT_POINTS = 2000
class ReduceFlights(CalculatorAction):
    #flights_amount,transportation_flights
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceFlights(inputs)
        return super().Eval(inputs)

class OffsetFlights(CalculatorAction):
    #flights_amount,offset_flights
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalOffsetFlights(inputs)
        return super().Eval(inputs)

class LowCarbonDiet(CalculatorAction):
    #eating_switch_meals,family_size,meat_frequency,eating_switch_meals_amount
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalLowCarbonDiet(inputs)
        return super().Eval(inputs)

class ReduceWaste(CalculatorAction):
    #reduce_waste,reuse_containers,buy_sell_used,buy_bulk,buy_recycled
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceWaste(inputs)
        return super().Eval(inputs)

class Compost(CalculatorAction):
    #compost_food_waste,compost_pickup
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalCompost(inputs)
        return super().Eval(inputs)

class ReduceLawnSize(CalculatorAction):
    #lawn_size,reduce_lawn_size,mower_type,mowing_frequency
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceLawnSize(inputs)
        return super().Eval(inputs)

class ReduceLawnCare(CalculatorAction):
    #lawn_size,lawn_service,mowing_frequency,mower_type,fertilizer,fertilizer_applications
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceLawnCare(inputs)
        return super().Eval(inputs)

class ElectricMower(CalculatorAction):
    #lawn_size,mower_type,mower_switch
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalElectricMower(inputs)
        return super().Eval(inputs)

class RakeOrElecBlower(CalculatorAction):
    #leaf_cleanup_gas_blower,leaf_cleanup_blower_switch
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalRakeOrElecBlower(inputs)
        return super().Eval(inputs)
