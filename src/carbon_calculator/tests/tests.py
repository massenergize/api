from django.test import TestCase, Client
from carbon_calculator.models import Action
from database.models import UserProfile
import json
import jsons
import os
from django.utils import timezone #For keeping track of when the consistency was last checked
from api.tests.common import signinAs

OUTPUTS_FILE   = "carbon_calculator/tests/expected_outputs.txt"
INPUTS_FILE    = "carbon_calculator/tests/allPossibleInputs.txt"
VALUE_DIFF     = "Value difference"

IMPORT_SUCCESS = {"status": True}


# Create your tests here.
class CarbonCalculatorTest(TestCase):
    @classmethod
    def setUpClass(self):
        self.client = Client()
        
        self.USER = UserProfile.objects.create(**{
          'full_name': "Regular User",
          'email': 'user@test.com',
        })

        self.CADMIN = UserProfile.objects.create(**{
          'full_name': "Community Admin",
          'email': 'cadmin@test.com',
          'is_community_admin': True
        })

        self.SADMIN = UserProfile.objects.create(**{
          'full_name': "Super Admin",
          'email': 'sadmin@test.com',
          'is_super_admin': True
        })

        signinAs(self.client, self.SADMIN)

        generate_inputs = eval(os.getenv("GENERATE_INPUTS"))
        if generate_inputs > 0:
            print("Generating Carbon Calculator input files")
            populate_inputs_file()
            self.input_data = []
        else:
            infile = os.getenv("TEST_INPUTS",default=INPUTS_FILE)
            print("Using input file: "+infile)
            self.input_data = self.read_inputs(self,infile)

        self.output_data = []
        self.differences = []

    @classmethod
    def tearDownClass(self):
        pass
        #print("tearDownClass")


    def test_info_actions(self):
        # test routes function
        # test there are actions
        # test that one action has the average_points

        response = self.client.get('/cc/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/cc/info')
        self.assertEqual(response.status_code, 200)

        #for some reason this URL doesn't want the trailing slash
        response = self.client.get('/cc/info/actions')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode('utf8'))
        data = data.get("data",data)
        self.assertGreaterEqual(len(data["actions"]),37)

        name= data["actions"][0]["name"]
        self.assertEqual(name,"energy_fair")

        points = data["actions"][0]["average_points"]
        self.assertEqual(points,15)

    def test_consistency(self):
        """
        Test if the results of all estimation calls match those of the last run.

        Get the inputs to each method from the INPUTS_FILE, as well as the
        previous outputs from the OUTPUTS_FILE. Call all methods of the carbon
        calculator with the inputs retrieved earlier, and compare the results
        with the results of the last run. Finally, pretty print the differences
        between this test run and the last one. Don't return anything.
        """
        #Check for required data
        if len(self.input_data) <= 0:
            return

        self.output_data = self.eval_all_actions(self.input_data)

        #Compare
        if len(self.input_data) != len(self.output_data):
            
            msg = "Consistency test: vector length mismatch, input = %d, output = %d" % (len(self.input_data), len(self.output_data))
            print(msg)
        self.differences = self.compare(self.input_data, self.output_data)

        self.pretty_print_diffs(
            self.differences,
            self.input_timestamp)

        numDifferences = len(self.differences)
        if numDifferences > 0:
            self.write_outputs(os.getenv("TEST_OUTPUTS",default=OUTPUTS_FILE))

        self.assertEqual(numDifferences,0)

    def read_inputs(self,filename):
        try:
            f = open(filename, 'r')
            header = eval(f.readline().strip())
            self.input_timestamp = header["Timestamp"]
            inputs = [eval(i.strip()) for i in f.readlines()]
            f.close()
        except Exception as e:
            inputs = []
            print("Exception from read_inputs: " + str(e))
        return inputs

    def write_outputs(self, filename):
        data = {"Timestamp": self.output_timestamp}
        outputLine(data,filename,True)

        for line in self.output_data:
            outputLine(line,filename,False)

    def eval_all_actions(self, inputs):
        """Run the estimate method of all the actions of the Carbon Calculator."""
        self.output_timestamp = timezone.now().isoformat(" ")   #Time of last test
        output_data = []
        for aip in inputs: #aip = action inputs pair
            try:
                outdata = jsons.loads( #Response of estimate in dict form
                        self.client.post(
                            "/cc/estimate/{}".format(aip['Action']), aip["inputs"]
                                ).content)
                outdata = outdata.get("data", outdata)

                output_data.append(
                    { "Action" : aip['Action'], 
                    "inputs" : aip['inputs'], 
                    'outputs' : outdata })
            except Exception as e: #Some may throw errors w/o inputs
                print('eval_all_inputs exception')
                print(e)
                print(aip)
        return output_data

    def compare(self, old, new):
        """
        Compare the old set of results with the new set.

        Populate a list of differences (tuples) according to the following rules:
        For a new action (action found in new results aggregate but not old)
        ("New action", ACTION_NAME)
        For a removed action (action found in old results aggregate but not new)
        ("Removed action", ACTION_NAME)
        For a differing value between the two aggregates
        ("Value difference", NEW_VALUE, OLD_VALUE)
        """
        differences = []

        for i in range(len(old)):
            action = old[i]["Action"]
            inputs = old[i]["inputs"]
            outputs_old = old[i]["outputs"]
            outputs_new = new[i]["outputs"]

            for key in ["status", "carbon_points", "cost", "savings"]:

                if not key in outputs_old:
                    print("outputs_old error:")
                    print(old[i])
                elif not key in outputs_new:
                    print("outputs_new error, key = "+key)
                    print(new[i])
                elif not outputs_new[key] == outputs_old[key]:
                    differences.append((action, inputs,
                        key,
                        outputs_old[key],
                        outputs_new[key]))
        return differences

    def pretty_print_diffs(self, diffs, oldtime):
        if len(diffs) > 0:
            hdr = "\ncarbon_calculator results inconsistent with input data from "+str(oldtime) + "\n# differences: %d\n======================================================" % len(diffs)
            print(hdr)
            for diff in diffs:
                print(str(diff)) #Not pretty yet
            print("\n")
        else:
            print("carbon_calculator results consistent with input data from "+str(oldtime))

    #extra
    def test_get_action_list(self):
        impact_info = self.client.get("/cc/info/actions", {})
        #print("actions:")
        #print(jsons.loads(impact_info.content))

    # 12 !!!!!! WORKS !!!!!!!
    def test_estimate_actions(self):

        obj = Action.objects.first()  # getting the first object in model
        field_object = Action._meta.get_field('name')  # this and next is getting the name
        field_value = field_object.value_from_object(obj)  # this returns actual name (as str)

        event_url = '/cc/estimate/' + field_value
        response = self.client.post(event_url, {})
        self.assertEqual(response.status_code, 200)
        # event_json = jsons.loads(event_info.content)
        # print(event_json)
        #test_action = self.client.post('/cc/estimate/')

    # 13 !!!!!! WORKS !!!!!!
    def test_undo_actions(self):

        obj = Action.objects.first()
        field_object = Action._meta.get_field('name')
        field_value = field_object.value_from_object(obj)
        #print(field_value)

        event_url = '/cc/undo/' + field_value
        response = self.client.post(event_url, {})
        #print(response)

    # 3 !!!!!! Works !!!!!!
    def test_impact_url(self):

       impact_info = self.client.get("/cc/info/impact", {})
       #print("test impact url")
       #print(jsons.loads(impact_info.content))

    # 5 !!!!!! WORKS !!!!!!!
    def test_info_group_url(self):
        #print("test info group url")
        group_info = self.client.get("/cc/info/groups", {})
        #print("test info group url")
        #print(jsons.loads(group_info.content))

    # 7 !!!! Works !!!!
    def test_info_stations_url(self):

        station_info = self.client.get("/cc/info/stations", {})
        #print("test info stations url")
        #print(jsons.loads(station_info.content))

    # 9 !!! Works But there is no users, I even checked by running the server
    def test_info_users_url(self):
        user_url = "/cc/info/users"

        user_info = self.client.get(user_url, {})
        #print("test info users url")
        #print(jsons.loads(user_info.content))

    # 11 !!!!! WORKS !!!!
    def test_create_user(self):
        response = self.client.post('/cc/users', {
                                                    'id':1,
                                                    'email':'email@gmail.com'
                                                 })
        data = jsons.loads(response.content)
        #print(data)

    # 10 DOES NOT WORK becuase there are no users
    def test_getting_user(self):
        response = self.client.get("/cc/info/users")
        #print(jsons.loads(response.content))

    # honestly no idea if this works, it gives a response that its exporting but idk if it is
    def test_exporting_csv(self):
        self.client.post('/cc/export',
                         {
                          "Defaults": "carbon_calculator/content/exportdefaults.csv"
                          })

def outputLine(data, filename, new=False):
    tag = "a"
    if new:
        tag = "w"

    f = open(filename, tag)
    f.write(str(data) + "\n")
    f.close()

def outputInputs(data):
    f = open("carbon_calculator/tests/Inputs.txt", "a")
    f.write(str(data) + "\n")
    f.close()

def populate_inputs_file():
    client      = Client()
    response    = client.get("/cc/info/actions")
    data        = jsons.loads(response.content)["actions"]
    names       = [i["name"] for i in data]

    filename_all = "carbon_calculator/tests/" + "allPossibleInputs.txt"
    data = {"Timestamp" : timezone.now().isoformat(" "), "Contents" : "All Possible Calculator Inputs"}
    outputLine(data, filename_all, True)
    filename_def = "carbon_calculator/tests/" + "defaultInputs.txt"
    data = {"Timestamp" : timezone.now().isoformat(" "), "Contents" : "Default Calculator Inputs"}
    outputLine(data, filename_def, True)
    np = 0    
    for name in names:
        # get info on the action to find allowed parameter values
        #print("URL: /cc/info/action/{}".format(name))
        response = client.get("/cc/info/action/{}".format(name))
        data = response.json() #jsons.loads(response.content, {})
        actionName = data["action"]["name"]

        questions = data["action"]["questionInfo"]
        qTot = []
        qInd = []
        for question in questions:
            qType = question["questionType"]
            qInd.append(0)
            if qType == "Choice":
                qTot.append(len(question["responses"]))
            else:
             if qType == "Number":
                qTot.append(1)
             else:
                qTot.append(0)

        nq = len(questions)
        qr = range(nq)
        done = False
        ni = 0
        while not done:
            actionPars = {"Action": actionName, "inputs":{}}
            q = 0
            for q in qr:
                question = questions[q]
                if qTot[q] > 1:
                    actionPars["inputs"][question["name"]] = question["responses"][qInd[q]]["text"]
                else:
                    if qTot[q] == 1:
                        val = 0.
                        typ = question["numeric_values"].get("typical_value",-999)
                        if typ > 0:
                            val = typ
                        actionPars["inputs"][question["name"]] = val

            outputs = client.get("/cc/estimate/{}".format(actionPars['Action']), actionPars["inputs"]).content.decode("utf-8")
            actionPars["outputs"] = eval(outputs)
            outputLine(actionPars, filename_all)
            np += 1
            ni += 1

            # update the response indices, increment one by one to get each combination
            for q in qr:
                if qTot[q]>0:
                    qInd[q] += 1
                    if qInd[q] == qTot[q]:
                        qInd[q] = 0
                    else:
                        break
                if q == nq-1:
                    done = True

        msg = "Action '%s', %d possible inputs" % (actionName, ni)
        print(msg)

    msg = "Number possible calculator inputs with all choices = %d" % np
    print(msg)
