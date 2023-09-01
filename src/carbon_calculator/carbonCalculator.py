# Carbon Calculator API
# Brad Hubbard-Nelson (bradhn@mindspring.com)
# Updated April 3
#imports
from datetime import datetime
#from .models import Action, Question, Event, Station, Group, ActionPoints, CarbonCalculatorMedia, Org
from .models import Action, Question, CarbonCalculatorMedia, CalcDefault
#from django.utils import timezone

from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
import csv
import requests
from .CCConstants import YES,NO, VALID_QUERY, INVALID_QUERY
from .CCDefaults import getDefault, getLocality, CCD
from .queries import QuerySingleAction
from .homeHeating import EvalEnergyAudit, EvalWeatherization, EvalProgrammableThermostats, EvalAirSourceHeatPump, \
                        EvalGroundSourceHeatPump, EvalHeatingSystemAssessment, EvalEfficientBoilerFurnace
from .electricity import EvalCommunitySolar, EvalRenewableElectricity, EvalLEDLighting, EvalEnergystarRefrigerator, \
                        EvalEnergystarWasher, EvalInductionStove, EvalHeatPumpDryer, EvalColdWaterWash, EvalLineDry, \
                        EvalRefrigeratorPickup, EvalSmartPowerStrip, EvalElectricityMonitor
from .solar import EvalSolarAssessment, EvalSolarPV
from .hotWater import EvalHotWaterAssessment, EvalHeatPumpWaterHeater, EvalSolarHW
from .transportation import EvalReplaceCar, EvalReduceMilesDriven, EvalEliminateCar, EvalReduceFlights, EvalOffsetFlights
from .foodWaste import EvalLowCarbonDiet, EvalReduceWaste, EvalCompost
from .landscaping import EvalReduceLawnSize, EvalReduceLawnCare, EvalRakeOrElecBlower, EvalElectricMower
#from .calcUsers import ExportCalcUsers, CalcUserUpdate

def SavePic2Media(picURL):
    if picURL == '':
        return None
    # in the import from AirTable, picture files have the url between ( ) after the original picture name
    loc1 = picURL.find('(')
    loc2 = picURL.find(')')
    if loc1>0 and loc2>0:
        picURL = picURL[loc1+1:loc2]
    #print("Importing picture from: "+picURL)
    try:
        resp = requests.get(picURL)
        if resp.status_code != requests.codes.ok:
            # Error handling here3
            # As of 2022, attachment URLs in AirTable expire after a couple of hour, so this will always fail until we figure out another solution
            # sprint("ERROR: Unable to import action photo from "+picURL)
            return None
        else:
            image = resp.content
            file_name =  picURL.split("/")[-1]
            file_type_ext = file_name.split(".")[-1]

            content_type = 'image/jpeg'
            if len(file_type_ext)>0 and file_type_ext.lower() == 'png':
                content_type = 'image/png'

            # Create a new Django file-like object to be used in models as ImageField using
            # InMemoryUploadedFile.  If you look at the source in Django, a
            # SimpleUploadedFile is essentially instantiated similarly to what is shown here
            img_io = BytesIO(image)
            image_file = InMemoryUploadedFile(img_io, None, file_name, content_type,
                                  None, None)

            media = CarbonCalculatorMedia.objects.create(file=image_file, name=f"{slugify(file_name)}")

            if media:
                media.save()
                return media
            else:
                return None
    except Exception as e:
        print("Error encountered: "+str(e))
        return None

def AverageImpact(action, date=None, locality="default"):
    averageName = action.name + '_average_points'
    return getDefault(locality, averageName, date)


class CarbonCalculator:
    def __init__(self, reset=False) :

        print("Initializing Carbon Calculator")
        # if no actions in database, import them
        if reset or Action.objects.count() == 0:

            # abnormal situation, except during testing or starting from blank database
            if not self.ImportAll():
                print("Error Initializing Carbon Calculator")
                return

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
                        'install_solarPV':InstallSolarPV,
                        'install_solarHW':InstallSolarHW,
                        'energystar_fridge':EnergystarRefrigerator,
                        'energystar_washer':EnergystarWasher,
                        'induction_stove':InductionStove,
                        'hp_dryer':HeatPumpDryer,
                        'coldwater_wash':ColdWaterWash,
                        'line_dry':LineDry,
                        'fridge_pickup':RefrigeratorPickup,
                        'smart_power_strip':SmartPowerStrip,
                        'electricity_monitor':ElectricityMonitor,
                        'replace_car':ReplaceCar,
                        'reduce_car_miles':ReduceMilesDriven,
                        'eliminate_car':EliminateCar,
                        'reduce_flights':ReduceFlights,
                        'offset_flights':OffsetFlights,
                        'low_carbon_diet':LowCarbonDiet,
                        'reduce_waste':ReduceWaste,
                        'compost':Compost,
                        'reduce_lawn_size':ReduceLawnSize,
                        'reduce_lawn_care':ReduceLawnCare,
                        'electric_mower':ElectricMower,
                        'rake_elec_blower':RakeOrElecBlower,
                        }


        # add any actions in database which don't yet have methods        
        #for action in Action.objects.filter(is_deleted=False):
        for action in Action.objects.all():
            name = action.name
            if not name in self.allActions.keys():
                self.allActions[name] = GenericUnspecifiedAction

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
            title = self.allActions[action].title
            description = self.allActions[action].description
            id = self.allActions[action].id
            points = self.allActions[action].average_points
            actionList.append( {'id': id, 'name':name, 'title':title, 'description':description, 'average_points':points} )
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

            try:
                results = theAction.Eval(inputs)
#                if save:
#                    results = self.RecordActionPoints(action,inputs,results)
                return results
            except Exception as error:
                print("Carbon Calculator exception")
                print(error)
                return queryFailed
        else:
            return queryFailed

    def Reset(self):

        self.__init__(reset=True)

        return False

    def ImportAll(self):
        print("Importing Carbon Calculator information")
        if not self.ImportQuestions('carbon_calculator/content/Questions.csv'):
            return False

        if not self.ImportActions('carbon_calculator/content/Actions.csv'):
            return False
        
        if not CCD.importDefaults(CCD, 'carbon_calculator/content/Defaults.csv'):
            return False
        
        return True

    # import via API
    def Import(self, inputs):
        if inputs.get('Confirm',NO) == YES:

            questionsFile = inputs.get('Questions','')
            if questionsFile!='':
                if not self.ImportQuestions(questionsFile):
                    return {"status":False}

            actionsFile = inputs.get('Actions','')
            if actionsFile!='':
                if not self.ImportActions(actionsFile):
                    return {"status":False}

            defaultsFile = inputs.get('Defaults','')
            if defaultsFile!='':
                if not CCD.importDefaults(CCD,defaultsFile):
                    return {"status":False}

            # all good
            return {"status":True}
        else:
            return {"status":False}
        
    def ImportQuestions(self, questionsFile):
        try:
            with open(questionsFile, newline='') as csvfile:
                inputlist = csv.reader(csvfile)
                first = True
                num = 0
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
                        #print('Importing Question ',question.name,': ',question.question_text)

                        if len(item)>19:
                            if len(item[16]):
                                question.minimum_value = eval(item[16])
                            if len(item[17])>0:
                                question.maximum_value = eval(item[17])
                            if len(item[18])>0:
                                question.typical_value = eval(item[18])

                        question.save()
                        num+=1
                msg = "Imported %d Carbon Calculator Questions" % num
                print(msg)
                csvfile.close()
            return True
        except Exception as e:
            print(str(e))
            print('Error importing Carbon Calculator questions')
            return False
        
    def ImportActions(self, actionsFile):
        try:
            with open(actionsFile, newline='') as csvfile:
                inputlist = csv.reader(csvfile)
                first = True
                num = 0
                for item in inputlist:
                    if first:
                        t = {}
                        for i in range(len(item)):
                            t[item[i]] = i
                        first = False
                    else:
                        name = item[0]
                        if name == '':
                            continue

                        qs = Action.objects.filter(name=name)
                        if qs:
                            qs[0].delete()

                        picture = None
                        if len(item)>=4 and name!='':
                            picture = SavePic2Media(item[t["Picture"]])
                            action = Action(name=item[0],
                                title = item[t["Title"]],
                                description=item[t["Description"]],
                                helptext=item[t["Helptext"]],
                                category=item[t["Category"]],
                                average_points=int(eval(item[t["Avg points"]])),
                                questions=item[t["Questions"]].split(","),
                                picture = picture)
                            action.save()

                            if name in self.allActions:
                                self.allActions[name].__init__(name)
                            num+=1
                msg = "Imported %d Carbon Calculator Actions" % num
                print(msg)
                csvfile.close()
            return True
        except Exception as e:
            print(str(e))
            print('Error importing Carbon Calculator actions')
            return False


    def Export(self,inputs):
        status = False
        defaultsFile = inputs.get('Defaults','')
        if defaultsFile!='':
            status = CCD.exportDefaults(CCD, defaultsFile)

        return {"status":status}

class CalculatorAction:
    def __init__(self,name):
        self.id = None
        self.name = name
        self.initialized = False
        self.title = "Action title"
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
        status, actionInfo = QuerySingleAction(self.name)
        if status == VALID_QUERY:
            self.id = actionInfo["id"]
            self.title = actionInfo["title"]
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

class GenericUnspecifiedAction(CalculatorAction):
    # a trivial bonus points action, part of registering for the energy fair
    # inputs: attend_fair,own_rent,fuel_assistance,activity_group
    def Eval(self, inputs):
        self.points = 0
        self.text = "This action does not have a calculation implemented."
        return super().Eval(inputs)

class EnergyFair(CalculatorAction):
    # a trivial bonus points action, part of registering for the energy fair
    # inputs: attend_fair,own_rent,fuel_assistance,activity_group
    def Eval(self, inputs):
        self.points = 0
        self.text = "You didn't attend the energy fair.  No points earned."
        if inputs.get('attend_fair',NO) == YES:
            #self.points = ENERGY_FAIR_POINTS

            locality = getLocality(inputs)
            self.points = getDefault(locality, 'energy_fair_average_points')

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

class ReplaceCar(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReplaceCar(inputs)
        return super().Eval(inputs)

class ReduceMilesDriven(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceMilesDriven(inputs)
        return super().Eval(inputs)

class EliminateCar(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalEliminateCar(inputs)
        return super().Eval(inputs)

class ReduceFlights(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceFlights(inputs)
        return super().Eval(inputs)

class OffsetFlights(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalOffsetFlights(inputs)
        return super().Eval(inputs)

class LowCarbonDiet(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalLowCarbonDiet(inputs)
        return super().Eval(inputs)

class ReduceWaste(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceWaste(inputs)
        return super().Eval(inputs)

class Compost(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalCompost(inputs)
        return super().Eval(inputs)

class ReduceLawnSize(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceLawnSize(inputs)
        return super().Eval(inputs)

class ReduceLawnCare(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalReduceLawnCare(inputs)
        return super().Eval(inputs)

class ElectricMower(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalElectricMower(inputs)
        return super().Eval(inputs)

class RakeOrElecBlower(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalRakeOrElecBlower(inputs)
        return super().Eval(inputs)
