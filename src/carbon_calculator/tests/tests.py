from django.test import TestCase, Client
from carbon_calculator.models import CalcUser, Event, Station, Action, Group, Question
from carbon_calculator.views import importcsv
from database.models import Vendor
import jsons
from carbon_calculator.solar import EvalSolarPV

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

    @classmethod
    def tearDownClass(self):
        print("tearDownClass")
        populate_inputs_file()

    def test_info_actions(self):
        # test routes function
        # test there are actions
        # test that one action has the average_points

        response = self.client.post('/cc')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/cc/info')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/cc/info/actions')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode('utf8'))
        self.assertGreaterEqual(len(data["actions"]),37)

        name= data["actions"][0]["name"]
        self.assertEqual(name,"energy_fair")

        points = data["actions"][0]["average_points"]
        self.assertEqual(points,50)

    def test_solarPVNoArgs(self):
        response = self.client.post('/cc/getInputs/install_solarPV', {})
        data = jsons.loads(response.content)
        #outputInputs(data)

    def test_solarPVGreat(self):
        response = self.client.post('/cc/getInputs/install_solarPV',
            {
            'solar_potential': 'Great'
            }
        )
        points, cost, savings, explanation = EvalSolarPV(response)
        outputs = {'points' : points,
                   'cost' : cost,
                   'savings' : savings,
                   'explanation' : explanation}
        data = jsons.loads(response.content)
        print(response)
        print(data)
        print(outputs)
        self.assertEqual(outputs['points'], 50)

def outputInputs(data, filename, new=False):
    tag = "a"
    if new:
        tag = "w"

    f = open("carbon_calculator/tests/"+filename, tag)
    f.write(str(data) + "\n")
    f.close()

def populate_inputs_file():
    client      = Client()
    response    = client.get("/cc/info/actions")
    data        = jsons.loads(response.content)["actions"]
    names       = [i["name"] for i in data]

    outputInputs("# All Possible Calculator Inputs", "allPossibleInputs.txt", True)
    outputInputs("# Default Calculator Inputs", "defaultInputs.txt", True)
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
            actionPars = {"Action": actionName}
            q = 0
            for q in qr:
                question = questions[q]
                if qTot[q] > 1:
                    actionPars[question["name"]] = question["responses"][qInd[q]]["text"]
                else:
                    if qTot[q] == 1:
                        actionPars[question["name"]] = 0

            outputInputs(actionPars, "allPossibleInputs.txt")
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
            outputInputs(
                jsons.loads(
                    client.post(
                        "/cc/getInputs/{}".format(name), {}
                        ).content
                    ),
                    'defaultInputs.txt'
                )
        except:
            pass

    msg = "Number possible calculator inputs with all choices = %d" % np
    print(msg)

"""Results from run with above settings:
Inputs to EvalSolarPV: {'solar_potential': 'Great'}
{'status': 0, 'carbon_points': 5251.0, 'cost': 14130.0, 'savings': 3241.0, 'explanation': 'installing a solar PV array on your home would pay back in around 5 years and save 26.3 tons of CO2 over 10 years.'}
.    """
