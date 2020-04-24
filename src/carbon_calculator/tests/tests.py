from django.test import TestCase, Client
from carbon_calculator.models import CalcUser, Event, Station, Action, Group, Question
from carbon_calculator.views import importcsv
from database.models import Vendor

#from carbon_calculator.carbonCalculator import CarbonCalculator

IMPORT_SUCCESS = {"status": True}
# Create your tests here.
class CarbonCalculatorTest(TestCase):
    def setUp(self):
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