# Carbon Calculator API
# Brad Hubbard-Nelson (bradhn@mindspring.com)
# Updated April 3
#imports
from datetime import date,datetime
from .models import Action,Question,Event,Station,Group,ActionPoints,CarbonCalculatorMedia,Org, Category, Subcategory
from django.utils import timezone

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
from .calcUsers import ExportCalcUsers, CalcUserUpdate
from .generic import EvalGenericCalculatorAction

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
            print("ERROR: Unable to import action photo from "+picURL)
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

class CarbonCalculator:
    def __init__(self) :
        print("carbon calc init")
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

    def AllActionsListExtra(self):
        response = {}
        actionList = []

        actions = Action.objects.filter() #no is_deleted field?
        for action in actions:
            name = action.name
            title = action.title
            description = action.description
            id = action.id
            points = action.average_points

            if action.category is None:
                category = ""
            else:
                category = action.category.name

            actionList.append( {'id': id, 'name':name, 'title':title, 'description':description, 'average_points':points, 'category': category,} ) #'category': category,
        categoryList =[]
        cats = Category.objects.filter(is_deleted=False)

        for category in cats:
            categoryList.append({'id': category.id, 'name': category.name})
        
        response['actions'] = actionList
        response['categories'] = categoryList
        response['status'] = VALID_QUERY
        return response
    
    def AllActionsList(self):
        response = {}
        actionList = []
   
        for action in self.allActions:
            name = self.allActions[action].name
            title = self.allActions[action].title
            description = self.allActions[action].description
            id = self.allActions[action].id
            points = self.allActions[action].average_points

            if self.allActions[action].category is None:
                category = ""
            else:

                #get category name from lookup!
                category = Category.objects.filter(id=self.allActions[action].category)[0].name

                #category = self.allActions[action].category.name
            actionList.append( {'id': id, 'name':name, 'title':title, 'description':description, 'average_points':points, 'category': category,} ) #'category': category,
        categoryList =[]
        cats = Category.objects.filter(is_deleted=False)
        print(cats)

        for category in cats:
            categoryList.append({'id': category.id, 'name': category.name})
        print(categoryList)
        
        response['actions'] = actionList
        response['categories'] = categoryList
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
                if save:
                    results = self.RecordActionPoints(action,inputs,results)
                return results
            except Exception as error:
                print("Carbon Calculator exception")
                print(error)
                return queryFailed
        else:
            return queryFailed

    def Undo(self, action, inputs):
# inputs is a dictionary of input parameters
        queryFailed = {'status':INVALID_QUERY}
        if action in self.allActions:
            user_id = inputs.pop("user_id",None)
            if user_id:
                record = ActionPoints.objects.filter(user_id=user_id,action=action).first()
                #if records:
                #    record = records.objects.filter(action=action).first()
                if record:
                        points = record.points
                        cost = record.cost
                        savings = record.savings
                        record.delete()

                        if CalcUserUpdate(user_id, {"points":-points, "cost":-cost, "savings":-savings}):
                            return {'status':VALID_QUERY, 'carbon_points':-points, 'cost':-cost, 'savings':-savings, 'explanation':"Undoing action"}
        return queryFailed

    def RecordActionPoints(self,action, inputs,results):
        queryFailed = {'status':INVALID_QUERY}
        user_id = inputs.pop("user_id",None)
        points = results.get("carbon_points",0.)
        cost = results.get("cost",0.)
        savings = results.get("savings",0.)
        record = ActionPoints(  user_id=user_id,
                                action=action,
                                choices=inputs,
                                points=points,
                                cost= cost,
                                savings = savings)
        record.save()

        if CalcUserUpdate(user_id, {"points":points, "cost":cost, "savings":savings}):
            return results
        return queryFailed

    def Reset(self,inputs):
        if inputs.get('Confirm',NO) == YES:
            print("Deleted Actions, Questions, Events and Stations")
            return {"status":True}
        else:
            return {"status":False}

    
    #don't want to import categories anymore
    """ def categories_import_helper(self, inputlist, first, num):
        for item in inputlist:
            if first:
                first = False
            else:
                if item[0] == '':
                    return first, num
                qs = Category.objects.filter(name=item[0])

                if len(item)>=1 and item[0]!='':
                    if not qs:

                        category = Category(
                                name=item[0],
                                is_deleted = True if item[1]== "True" else False,
                                description = item[2],
                                )
                        category.save()
                        num+=1
                    else:
                        qs.update(
                                is_deleted = True if item[1]== "True" else False,
                                description = item[2],
                                )
                        num+=1

        return first, num """
    
    def subcategories_import_helper(self, inputlist, first, num):
        for item in inputlist:
            if first:
                first = False
            else:
                if item[0] == '':
                    return first, num
                
                cat = Category.objects.filter(name=item[1]).first()
                if cat: 
                    qs = Subcategory.objects.filter(name=item[0], category = cat)

                    if len(item)>=1 and item[0]!='':

                        #do we only want it for categories where is_deleted=False? or set to is_deleted too?
                        cat = Category.objects.filter(name=item[1]).first()
                        
                        if cat:
                            cat_is_deleted = cat.is_deleted
                            if not qs: 
                                subcategory = Subcategory(
                                        name=item[0],
                                        is_deleted = True if cat_is_deleted == True else True if item[2]== "True" else False,
                                        description = item[3],
                                        category = cat,
                                        )
                                subcategory.save()
                                num+=1
                            elif qs:
                                qs.update(
                                    is_deleted = True if cat_is_deleted == True else True if item[2]== "True" else False,
                                    description = item[3],
                                )
                if not cat:
                    print("Did not make subcategory for " + str(item[0]))
        return first, num
    
    def actions_import_helper(self, inputlist, first, num):
        for item in inputlist:
            if first:
                t = {}
                for i in range(len(item)):
                    t[item[i]] = i
                first = False
            else:
                name = item[0]
                if name == '':
                    return first, num

                qs = Action.objects.filter(name=name)

                picture = None
                #why len greater than or equal to 4??
                if len(item)>=4 and name!='':
                    #filter by is_deleted?
                    cat = Category.objects.filter(name=item[t["Category"]]).first()
                    subcat = Subcategory.objects.filter(name=item[t["Subcategory"]], category = cat).first()      

                    if cat and not qs:
                        picture = SavePic2Media(item[t["Picture"]])
                        action = Action(name=name,
                            title = item[t["Title"]],
                            description=item[t["Description"]],
                            helptext=item[t["Helptext"]],
                            old_category=item[t["Old Category"]], 
                            average_points=int(eval(item[t["Avg points"]])),
                            questions=item[t["Questions"]].split(","),
                            picture = picture,
                            category = cat,
                            sub_category = subcat,
                            )
                        action.save()
                        if name in self.allActions:
                            self.allActions[name].__init__(name)
                        # else: 
                        #     self.allActions[name].__init__(EvalGenericCalculatorAction)
                        num+=1
                    
                    elif cat and qs:
                        qs.update(
                            title = item[t["Title"]],
                            description=item[t["Description"]],
                            helptext=item[t["Helptext"]],
                            old_category=item[t["Old Category"]], 
                            average_points=int(eval(item[t["Avg points"]])),
                            questions=item[t["Questions"]].split(","),
                            picture = picture,
                            category = cat,
                            sub_category = subcat,
                            )
                            
                        if name in self.allActions:
                            self.allActions[name].__init__(name)
                        # else:
                        #     self.allActions[name].__init__(EvalGenericCalculatorAction)
                            #num+=1 ?

                    if not cat:
                        print("Did not make action for " + str(item[0]))
           
        return first, num

    def import_helper(self, inputs, string, status, method):
        data_file = inputs.get(string, '')
        if data_file != '':
            with open(data_file, newline='') as csvfile:
                inputlist = csv.reader(csvfile)
                first = True
                num = 0

                first, num = method(inputlist, first, num)

                msg = "Imported %d Carbon Calculator %s" % (num, string)
                print(msg)
                csvfile.close()
                status = True
        return status

    
    def Import(self,inputs):
        if inputs.get('Confirm',NO) == YES:
            status = False

            status = self.import_helper(inputs, "Subcategories", status, self.subcategories_import_helper)
            #status = self.import_helper(inputs, "Categories", status, self.categories_import_helper)
            status = self.import_helper(inputs, "Actions", status, self.actions_import_helper)

            """ questionsFile = inputs.get('Questions','')
            if questionsFile!='':
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
                    status = True 


            status = self.import_helper(inputs, "Actions", status, self.actions_import_helper)

            stationsFile = inputs.get('Stations','')
            if stationsFile!='':
                with open(stationsFile, newline='') as csvfile:
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

                            qs = Station.objects.filter(name=item[0])
                            if qs:
                                qs[0].delete()

                            station_icon = SavePic2Media(item[3])

                            station = Station(name=item[0],
                                displayname=item[1],
                                description=item[2],
                                icon = station_icon,
                                actions=item[5].split(","))

                            #print('Importing Station ',station.name,': ',station.description)
                            station.save()
                            num+=1
                    msg = "Imported %d CarbonSaver Stations" % num
                    print(msg)
                    csvfile.close()
                    status = True

            groupsFile = inputs.get('Groups','')
            if groupsFile!='':
                with open(groupsFile, newline='') as csvfile:
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

                            #print('Importing Group ',group.displayname)
                            group.save()
                            num+=1
                    msg = "Imported %d CarbonSaver Groups" % num
                    print(msg)
                    csvfile.close()
                    status = True

            orgsFile = inputs.get('Organizations','')
            if orgsFile!='':
                with open(orgsFile, newline='') as csvfile:
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
                            qs = Org.objects.filter(name=item[0])
                            if qs:
                                qs[0].delete()

                            logo = None
                            logo = SavePic2Media(item[6])
 
                             #if action[5]!='':
                            #    import this media filt
                            #    actionPicture = Media()
                            org = Org(name=item[0],
                                contact=item[1],
                                email = item[2],
                                phone = item[3],
                                about = item[4],
                                url = item[5],
                                logo = logo
                                )

                            #print('Importing Group ',group.displayname)
                            org.save()
                            num+=1
                    msg = "Imported %d CarbonSaver Orgs" % num
                    print(msg)
                    csvfile.close()
                    status = True

            eventsFile = inputs.get('Events','')
            if eventsFile!='':
                with open(eventsFile, newline='') as csvfile:
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
                            qs = Event.objects.filter(name=item[0])
                            if qs:
                                qs[0].delete()

                            eventdate = item[2]
                            if eventdate != '':
                                dt = datetime.strptime(item[2].upper(), '%m/%d/%Y %H:%M%p')
                                current_tz = timezone.get_current_timezone()
                                dt = current_tz.localize(dt)
                            else:
                                dt= ''
                            groupslist = None
                            if item[5]!='':
                                groupslist = item[5].split(",")

                            # for now assume just one host org and one sponsor org
                            host_orgs = Org.objects.filter(name=item[6])
                            host_org = None
                            if host_orgs:
                                host_org = host_orgs[0]

                                
                            sponsor_orgs = Org.objects.filter(name=item[7])
                            sponsor_org = None
                            if sponsor_orgs:
                                sponsor_org = sponsor_orgs[0]

                            visible = False
                            if item[8]=="checked":
                                visible = True

                            event = Event(name=item[0],
                                displayname=item[1],
                                location = item[3],
                                stationslist = item[4].split(","),
                                visible = visible,
                                event_tag = item[9]
                                )
                            if dt != '':
                                event.datetime = dt

                            event.save()
                            if groupslist:
                                for group in groupslist:
                                    g = Group.objects.filter(name=group)
                                    if g:
                                        gg = g[0]
                                        event.groups.add(gg)

                            if host_org:
                                event.host_org.add(host_org)
                            if sponsor_org:
                                event.sponsor_org.add(sponsor_org)

                            #print('Importing Event ',event.name,' at ',event.location,' on ',event.datetime)
                            event.save()
                            num+=1
                    msg = "Imported %d CarbonSaver Events" % num
                    print(msg)
                    csvfile.close()
                    status = True """
            # defaultsFile = inputs.get('Defaults','')
            # if defaultsFile!='':
            #     status = CCD.importDefaults(CCD,defaultsFile)

            self.__init__()
            return {"status":status}
        else:
            return {"status":False}

    def Export(self,inputs):
        status = False
        defaultsFile = inputs.get('Defaults','')
        if defaultsFile!='':
            status = CCD.exportDefaults(CCD, defaultsFile)

        usersFile = inputs.get('Users','')
        if usersFile!='':
            event = inputs.get('Event','')
            status = ExportCalcUsers(usersFile, event)
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
        self.category = None

        status, actionInfo = QuerySingleAction(self.name)

        #print(actionInfo["category"])
        if status == VALID_QUERY:
            self.id = actionInfo["id"]
            self.title = actionInfo["title"]
            self.description = actionInfo["description"]
            self.helptext = actionInfo["helptext"]
            self.questions = actionInfo["questionInfo"]    # question with list of valid responses.
            self.average_points = actionInfo["average_points"]
            self.picture = actionInfo["picture"]
            self.initialized = True
            self.category = actionInfo["category"]

    def Query(self):
        print("individual calc action Query")
        status, actionInfo = QuerySingleAction(self.name)
        return {"status":status, "action":actionInfo}

    def Eval(self, inputs):
        return {'status':VALID_QUERY, 'carbon_points':round(self.points,0), 'cost':round(self.cost,0), 'savings':round(self.savings,0), 'explanation':self.text}

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

class GenericCalculatorAction(CalculatorAction):
    def Eval(self, inputs):
        self.points, self.cost, self.savings, self.text = EvalGenericCalculatorAction(inputs)
        return super().Eval(inputs)
