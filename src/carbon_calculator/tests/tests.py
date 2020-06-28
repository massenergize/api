from django.test import TestCase, Client
from carbon_calculator.models import CalcUser, Event, Station, Action, Group, Question
from carbon_calculator.views import importcsv
import json
import jsons
import os

IMPORT_SUCCESS = {"status": True}
# Create your tests here.
class CarbonCalculatorTest(TestCase):
    @classmethod
    def setUpClass(self):
        self.client = Client()
        self.client.post('/cc/import',
            {   "Confirm": "Yes",
                "Actions":"carbon_calculator/content/Actions.csv",
                "Questions":"carbon_calculator/content/Questions.csv",
                "Stations":"carbon_calculator/content/Stations.csv",
                "Groups":"carbon_calculator/content/Groups.csv",
                "Events":"carbon_calculator/content/Events.csv",
                "Defaults":"carbon_calculator/content/exportdefaults.csv"
                })


        self.input_data = read_inputs(os.getenv("TEST_INPUTS"))
        self.output_data = []

    @classmethod
    def tearDownClass(self):
        print("tearDownClass")

        generate_inputs = eval(os.getenv("GENERATE_INPUTS"))
        if generate_inputs > 0:
            print("Generating Carbon Calculator input files")
            populate_inputs_file()

        else:
            write_outputs(os.getenv("TEST_OUTPUTS"))

    def test_info_actions(self):
        # test routes function
        # test there are actions
        # test that one action has the average_points

        response = self.client.get('/cc')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/cc/info')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/cc/info/actions')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode('utf8'))
        self.assertGreaterEqual(len(data["actions"]),37)

        name= data["actions"][0]["name"]
        self.assertEqual(name,"energy_fair")

        points = data["actions"][0]["average_points"]
        self.assertEqual(points,50)

    #def test_solarPVNoArgs(self):
    #    response = self.client.post('/cc/getInputs/install_solarPV', {})
    #    data = jsons.loads(response.content)
    #    #outputInputs(data)

    #def test_solarPVGreat(self):
    #    response = self.client.post('/cc/getInputs/install_solarPV',
    #        {
    #        'solar_potential': 'Great'
    #        }
    #    )
    #    data = jsons.loads(response.content)

def outputLine(data, filename, new=False):
    tag = "a"
    if new:
        tag = "w"

    f = open(filename, tag)
    f.write(str(data) + "\n")
    f.close()

def read_inputs(filename):
    data = []
    return data

def write_outputs(filename):
    outputLine(data,filename,True)


def populate_inputs_file():
    client      = Client()
    response    = client.get("/cc/info/actions")
    data        = jsons.loads(response.content)["actions"]
    names       = [i["name"] for i in data]

    filename_all = "carbon_calculator/tests/" + "allPossibleInputs.txt"
    outputLine("# All Possible Calculator Inputs", filename_all, True)
    filename_def = "carbon_calculator/tests/" + "defaultInputs.txt"
    outputLine("# Default Calculator Inputs", filename_def, True)
    np = 0    
    for name in names:
        # get info on the action to find allowed parameter values
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
            if ni<10:
                print(outputs)
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

        #generate the default values list
        try:
            outputLine(
                jsons.loads(
                    client.post(
                        "/cc/getInputs/{}".format(name), {}
                        ).content
                    ),
                    filename_def
                )
        except:
            pass

    msg = "Number possible calculator inputs with all choices = %d" % np
    print(msg)

"""Results from run with above settings:
Inputs to EvalSolarPV: {'solar_potential': 'Great'}
{'status': 0, 'carbon_points': 5251.0, 'cost': 14130.0, 'savings': 3241.0, 'explanation': 'installing a solar PV array on your home would pay back in around 5 years and save 26.3 tons of CO2 over 10 years.'}
.    """
