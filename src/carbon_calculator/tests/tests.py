from django.test import TestCase, Client
from carbon_calculator.models import CalcUser, Event, Station, Action, Group, Question
from carbon_calculator.views import importcsv
from database.models import Vendor
import jsons

#from carbon_calculator.carbonCalculator import CarbonCalculator

IMPORT_SUCCESS = {"status": True}
# Create your tests here.
class CarbonCalculatorTest(TestCase):
    have_imported = False
    #@classmethod
    def setUp(self): #CHANGE TO SETUPCLASS LATER
        self.client = Client()
        self.importdata()

        #CalcUser.objects.create(first_name='first_name',
        #                    last_name = 'name',
        #                    email ='name@gmail.com',
        #                    locality = 'SometownMA',
        #                    minimum_age = True,
        #                    accepts_terms_and_conditions = True)
        #Animal.objects.create(name="cat", sound="meow")

    def importdata(self):
        if CarbonCalculatorTest.have_imported:
            return
        CarbonCalculatorTest.have_imported = True
        response = self.client.post('/cc/import',
            {   "Confirm": "Yes",
                "Actions":"carbon_calculator/content/Actions.csv",
                "Questions":"carbon_calculator/content/Questions.csv",
                "Stations":"carbon_calculator/content/Stations.csv",
                "Groups":"carbon_calculator/content/Groups.csv",
                "Events":"carbon_calculator/content/Events.csv"
                })
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/cc/import',
            {   "Confirm": "Yes",
                "Defaults":"carbon_calculator/content/exportdefaults.csv"
                })
        self.assertEqual(response.status_code, 200)

    def test_info_actions(self):
        response = self.client.post('/cc/info/actions')
        self.assertEqual(response.status_code, 200)

    def test_solarPV(self):
        response = self.client.post('/cc/estimate/install_solarPV',
        {
            'solar_potential': 'Great'
            }
        )
        data = jsons.loads(response.content)
        print(data)
        self.assertEqual(data['status'], 0) #If there was an internal error

        """Results from run with above settings:
Inputs to EvalSolarPV: {'solar_potential': 'Great'}
{'status': 0, 'carbon_points': 5251.0, 'cost': 14130.0, 'savings': 3241.0, 'explanation': 'installing a solar PV array on your home would pay back in around 5 years and save 26.3 tons of CO2 over 10 years.'}
.    """
