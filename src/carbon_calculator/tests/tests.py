from django.test import TestCase, Client
from carbon_calculator.models import CalcUser, Event, Station, Action, Group, Question
from carbon_calculator.views import importcsv
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
        response = self.client.post('/cc/import', { "Confirm": "Yes", "Questions":"carbon_calculator/content/Questions.csv"})
        self.assertEqual(response, IMPORT_SUCCESS)

        response = self.client.post('/cc/import', { "Confirm": "Yes", "Actions":"carbon_calculator/content/Actions.csv"})
        self.assertEqual(response, IMPORT_SUCCESS)

        response = self.client.post('/cc/import', { "Confirm": "Yes", "Stations":"carbon_calculator/content/Stations.csv"})
        self.assertEqual(response, IMPORT_SUCCESS)

        response = self.client.post('/cc/import', { "Confirm": "Yes", "Groups":"carbon_calculator/content/Groups.csv"})
        self.assertEqual(response, IMPORT_SUCCESS)

        response = self.client.post('/cc/import', { "Confirm": "Yes", "Events":"carbon_calculator/content/Events.csv"})
        self.assertEqual(response, IMPORT_SUCCESS)
