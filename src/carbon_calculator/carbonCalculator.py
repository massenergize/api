# Carbon Calculator API
# Brad Hubbard-Nelson (bradhn@mindspring.com)
# Updated April 3
#imports
import csv
import os
import time
from datetime import date, datetime
from io import BytesIO

import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify

from _main_.settings import BASE_DIR, RUN_SERVER_LOCALLY
from _main_.utils.common import custom_timezone_info
from .CCConstants import INVALID_QUERY, NO, VALID_QUERY, YES
from .CCDefaults import CCD, getDefault, getLocality
from .electricity import EvalColdWaterWash, EvalCommunitySolar, EvalElectricityMonitor, EvalEnergystarRefrigerator, \
    EvalEnergystarWasher, EvalHeatPumpDryer, EvalInductionStove, EvalLEDLighting, EvalLineDry, EvalRefrigeratorPickup, \
    EvalRenewableElectricity, EvalSmartPowerStrip
from .foodWaste import EvalCompost, EvalLowCarbonDiet, EvalReduceWaste
from .homeHeating import EvalAirSourceHeatPump, EvalEfficientBoilerFurnace, EvalEnergyAudit, EvalGroundSourceHeatPump, \
    EvalHeatingSystemAssessment, EvalProgrammableThermostats, EvalWeatherization
from .hotWater import EvalHeatPumpWaterHeater, EvalHotWaterAssessment, EvalSolarHW
from .landscaping import EvalElectricMower, EvalRakeOrElecBlower, EvalReduceLawnCare, EvalReduceLawnSize
from .models import Action, CarbonCalculatorMedia, Category, Question, Subcategory, Version
from .queries import QuerySingleAction
from .solar import EvalSolarAssessment, EvalSolarPV
from .transportation import EvalEliminateCar, EvalOffsetFlights, EvalReduceFlights, EvalReduceMilesDriven, \
    EvalReplaceCar

CALCULATOR_VERSION = "4.0.5"
QUESTIONS_DATA = BASE_DIR + "/carbon_calculator/content/Questions.csv"
ACTIONS_DATA = BASE_DIR + "/carbon_calculator/content/Actions.csv"
CATEGORIES_DATA = BASE_DIR + "/carbon_calculator/content/Categories.csv"
SUBCATEGORIES_DATA = BASE_DIR + "/carbon_calculator/content/Subcategories.csv"
DEFAULTS_DATA = BASE_DIR + "/carbon_calculator/content/defaults.csv"
TOKEN_POINTS = 15

def fileDateTime(path):
    # file modification
    timestamp = os.path.getmtime(path)
    utc=custom_timezone_info()

    # convert timestamp into DateTime object
    datestamp = datetime.fromtimestamp(timestamp).replace(tzinfo=utc)
    return datestamp

def versionCheck():
    version = Version.objects.all()
    if not version:
        version = Version.objects.create(version=CALCULATOR_VERSION, note="Initial Version")
        print(version.note)
        return False    # reload data
    else:
        version = version.latest('id')

    # update based on date of most recent data file
    files_updated = max(fileDateTime(QUESTIONS_DATA),
                       fileDateTime(ACTIONS_DATA),
                       fileDateTime(DEFAULTS_DATA))

    today = str(date.today())
    if version.version != CALCULATOR_VERSION: 
        version.version = CALCULATOR_VERSION
        version.note = "Calculator version update on "+today
        print(version.note)
        version.save()
        return False    # reload data
    elif version.updated_on < files_updated:
        version.note = "Calculator data update on "+today
        print(version.note)
        version.save()
        return False    # reload data
    return True

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


def getCarbonImpact(action, done_only=True): 
  
    if not action: return 0

    if hasattr(action, "status"):
        # this is a UserActionRel for a completed or todo action
        if done_only and action.status !="DONE":  return 0

        household = action.real_estate_unit
        if household.address:
            loc_options = locality_options(action.real_estate_unit.address.simple_json())
        else:
            if household.community:
                location = household.community.locations.first().simple_json()
                loc_options = locality_options(location)
            else:    
                loc_options = []   
        if action.action and action.action.calculator_action:
            return AverageImpact(action.action.calculator_action, action.date_completed, loc_options)
        else:
            return action.carbon_impact

    elif hasattr(action, "calculator_action"):
        # This is an Action posted by the community.  In this case we use the community location (community.locations)
        location = action.community.locations.first().simple_json()
        loc_options = locality_options(location)
        if action.calculator_action:
            return AverageImpact(action.calculator_action, None, loc_options)
        else:
            return 0
    else:
        return 0

def AverageImpact(action, date=None, loc_options=[]):
    averageName = action.name + '_average_points'
    impact = getDefault(loc_options, averageName, date, default=TOKEN_POINTS)
    return impact


def locality_options(loc):
    # for actions which have been completed, use RealEstateUnit location
    # for actions posted by communities, but not done we use the Community location
    # return options in precedence order: city, county, state, i.e. ["Concord-MA", "Middlesex County-MA", "MA"]
    options = []
    if type(loc) == dict:
        city = loc.get("city")
        county = loc.get("county")
        state = loc.get("state")
        if city and state:
            options.append(city + "-" + state)
            if county:
                options.append(county + "-" + state)
            options.append(state)
        return options
    # not usual:
    # invalid location information, use default
    print("carbon calculator: Locality type = "+str(type(loc))+ " loc = "+str(loc))
    return []


class CarbonCalculator:
    
    def __init__(self, reset=False) :

        start = time.time()
        try:
            print("Initializing Carbon Calculator, version "+CALCULATOR_VERSION)

            # check version, reload if version or data has been updated
            if not versionCheck():
                reset = True

            # reload data if starting from blank database or data version update
            if reset:
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

            end = time.time()
            if RUN_SERVER_LOCALLY:
                print("Carbon Calculator initialization time: "+str(end - start)+" seconds")

        except Exception as e:
            print(str(e))
            print("Calculator initialization skipped")


    # query actions
    def Query(self,action=None):
        if action in self.allActions:
            return self.allActions[action].Query()
        else:
            return self.AllActionsList()
    
    def AllActionsList(self):
        response = {}
        actionList = []
   
        #for action in self.allActions:
        actions = Action.objects.filter() #no is_deleted field?
        for action in actions:
            theAction = self.allActions.get(action,None)
            if theAction and not theAction.initialized:
                ret = theAction.Query()
                if ret["status"] != VALID_QUERY:
                    print("Action " + theAction.name + " initialization failed")
                    return ret
                
            name = action.name
            title = action.title
            description = action.description
            id = action.id
            points = action.average_points

            # category = action.category.name if action.category else ""
            # subcategory = action.sub_category.name if action.sub_category else ""

            actionList.append( {'id': id, 'name':name, 'title':title, 'description':description, 'average_points':points, 'category': action.category.simple_json() if action.category else None, 'subcategory': action.sub_category.simple_json() if action.sub_category else None} ) 

        categoryList = []
        cats = Category.objects.filter(is_deleted=False)
        for category in cats:
            # categoryList.append({'id': category.id, 'name': category.name})
            categoryList.append(category.simple_json())

        subcatList = []
        subcats = Subcategory.objects.filter(is_deleted=False)
        for subcat in subcats:
            subcatList.append(subcat.simple_json())
            # subcatList.append({'id': subcat.id, 'name': subcat.name, "category":subcat.category.name if subcat.category else None, "category_id": subcat.category.id if subcat.category else None})
        
        response['actions'] = actionList
        response['categories'] = categoryList
        response["subcategories"] = subcatList
        response['status'] = VALID_QUERY
        return response

    def Estimate(self, action, inputs, save=False):
# inputs is a dictionary of input parameters
        queryFailed = {'status':INVALID_QUERY}
        if action in self.allActions:
            theAction = self.allActions[action] # Might throw keyError
            if not theAction.initialized:       # this initializes the calculation if not done previously
                ret = self.allActions[action].Query()    # Might throw keyError
                if ret["status"] != VALID_QUERY:
                    print("Action " + theAction.name + " initialization failed")
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
            print("action not in allActions")
            return queryFailed

    def Reset(self):

        self.__init__(reset=True)

        return False

    def ImportAll(self):
        print("Importing Carbon Calculator information")
        if not self.ImportQuestions(QUESTIONS_DATA):
            return False

        if not self.ImportSubcategories(SUBCATEGORIES_DATA):
            return False
        
        if not self.ImportActions(ACTIONS_DATA):
            return False
        
        if not CCD.importDefaults(CCD, DEFAULTS_DATA):
            return False
        
        return True

    
    def subcategories_import_helper(self, inputlist, first, update_num, import_num):
        for item in inputlist:
            if first:
                first = False
            else:
                if item[0] == '':
                    return first, update_num, import_num
                
                subcategory_name = item[0]
                category_name = item[1]

                cat = Category.objects.filter(name=category_name).first()
                if not cat:
                    cat = Category.objects.create(name=category_name)

                if cat: 
                    qs = Subcategory.objects.filter(name=subcategory_name, category = cat)
                    if not qs: 
                        subcategory = Subcategory.objects.create(
                            name=subcategory_name,
                            description = item[3],
                            category = cat,
                        )
                        import_num+=1
                    elif qs:
                        qs.update(
                            description = item[3],
                        )
                        update_num +=1

                else:
                    print("Did not make subcategory for " + str(subcategory_name))

        return first, update_num, import_num
    
    def actions_import_helper(self, inputlist, first, update_num, import_num):
        for item in inputlist:
            if first:
                t = {}
                for i in range(len(item)):
                    t[item[i]] = i
                first = False
            else:
                name = item[0]
                if name == '':
                    return first, update_num, import_num

                qs = Action.objects.filter(name=name)

                picture = None
                #why len greater than or equal to 4??
                if len(item)>=4 and name!='':
                    #filter by is_deleted?
                    cat = Category.objects.filter(name=item[t["Category"]]).first()
                    subcat = Subcategory.objects.filter(name=item[t["Subcategory"]], category = cat).first()      

                    if cat and not qs:
                        action = Action(name=name,
                            title = item[t["Title"]],
                            description=item[t["Description"]],
                            helptext= "" if not item[t["Helptext"]] else "",
                            average_points=0 if not item[t["Avg points"]] else int(eval(item[t["Avg points"]])),
                            questions=item[t["Questions"]].split(","),
                            picture = picture,
                            category = cat,
                            sub_category = subcat,
                            )
                    
                        if name in self.allActions:
                            self.allActions[name].__init__(name)
                        import_num+=1
                    
                    elif cat and qs:
                        qs.update(
                            title = item[t["Title"]],
                            description=item[t["Description"]],
                            helptext=item[t["Helptext"]],
                            average_points= 0 if not item[t["Avg points"]] else int(eval(item[t["Avg points"]])),
                            questions=item[t["Questions"]].split(","),
                            picture = picture,
                            category = cat,
                            sub_category = subcat,
                            )
                        update_num +=1
                        if name in self.allActions:
                            self.allActions[name].__init__(name)

                    if not cat:
                        print("Did not make action for " + str(item[0]))
           
        return first, update_num, import_num

    def import_helper(self, inputs, string, status, method):
        try:
            data_file = inputs.get(string, '')
            if data_file != '':
                with open(data_file, newline='') as csvfile:
                    inputlist = csv.reader(csvfile)
                    first = True
                    import_num = 0
                    update_num = 0
                    first, update_num, import_num = method(inputlist, first, import_num, update_num)

                    import_msg = "Imported %d Carbon Calculator %s \n" % (import_num, string)
                    update_msg = "Updated %d Carbon Calculator %s" % (update_num, string)
                    print(import_msg + update_msg)
                    csvfile.close()
                    return True
        except Exception as e:
            print(str(e))
            return False

    
    def Import(self,inputs):
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

                        skip = [[],[],[],[],[],[]]
                        for i in range(6):
                            ii = 5+2*i
                            if item[ii]!='' :
                                skip[i] = item[ii].split(",")

                        minimum_value = maximum_value = typical_value = None
                        if len(item)>19:
                            if len(item[16]):
                                minimum_value = eval(item[16])
                            if len(item[17])>0:
                                maximum_value = eval(item[17])
                            if len(item[18])>0:
                                typical_value = eval(item[18])

                        # update the unique Question with this name
                        qs, created = Question.objects.update_or_create(
                            name=item[0],
                            defaults={
                                'category':item[1],
                                'question_text':item[2],
                                'question_type':item[3],
                                'response_1':item[4], 'skip_1':skip[0],
                                'response_2':item[6], 'skip_2':skip[1],
                                'response_3':item[8], 'skip_3':skip[2],
                                'response_4':item[10], 'skip_4':skip[3],
                                'response_5':item[12], 'skip_5':skip[4],
                                'response_6':item[14], 'skip_6':skip[5],
                                'minimum_value':minimum_value,
                                'maximum_value':maximum_value,
                                'typical_value':typical_value
                            }
                        )

                        if created:
                            num += 1

                if num>0:
                    msg = "Imported %d Carbon Calculator Questions" % num
                else:
                    msg = "Updated Carbon Calculator Questions from import"
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
                reader = csv.reader(csvfile)
                num = 0

                # dictionary of column indices by heading
                column_index = {}
                headers = next(reader, None)
                for index in range(len(headers)):
                    heading = headers[index] if index!=0 else 'Name'
                    column_index[heading] = index

                for item in reader:
                    name = item[0]
                    if name == '':
                        continue
                    avg_points = item[column_index["Avg points"]]
                    cat = Category.objects.filter(name=item[column_index["Category"]]).first()
                    subcat = Subcategory.objects.filter(name=item[column_index["Subcategory"]], category = cat).first() 

                    defaults = {
                            'title':item[column_index["Title"]],
                            'description':item[column_index["Description"]],
                            'helptext':item[column_index["Helptext"]],
                            'category':cat,
                            'sub_category':subcat,
                            'average_points': int(eval(avg_points)) if avg_points else TOKEN_POINTS,
                            'questions':item[column_index["Questions"]].split(",")
                        }

                    # update the unique Action with this name
                    qs, created = Action.objects.update_or_create(
                        name=name,
                        defaults=defaults
                    )
                    
                    if created:
                        num += 1

                if num:
                    msg = "Imported %d Carbon Calculator Actions" % num
                else:
                    msg = "Updated Carbon Calculator Actions from import"
                print(msg)
                csvfile.close()
            return True
        except Exception as e:
            print(str(e))
            print('Error importing Carbon Calculator actions')
            return False


    def ImportSubcategories(self, inputfile):
        return self.import_helper({'Subcategories': inputfile}, "Subcategories", True, self.subcategories_import_helper)


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

    def Query(self):
        status, actionInfo = QuerySingleAction(self.name)
        if not self.id and status == VALID_QUERY:
            self.id = actionInfo["id"]
            self.title = actionInfo["title"]
            self.description = actionInfo["description"]
            self.helptext = actionInfo["helptext"]
            self.questions = actionInfo["questionInfo"]    # question with list of valid responses.
            self.average_points = actionInfo["average_points"]
            self.picture = actionInfo["picture"]
            self.initialized = True
            self.category = actionInfo["category"]

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
