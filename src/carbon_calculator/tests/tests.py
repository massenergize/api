from django.test import TestCase
from carbon_calculator.models import CalcUser, Event, Station, Action, Group, Question
from carbon_calculator.views import importcsv
#from carbon_calculator.carbonCalculator import CarbonCalculator

# Create your tests here.
class EventTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        #CalcUser.objects.create(first_name='first_name',
        #                    last_name = 'name',
        #                    email ='name@gmail.com', 
        #                    locality = 'SometownMA',
        #                    minimum_age = True,
        #                    accepts_terms_and_conditions = True)
        #Animal.objects.create(name="cat", sound="meow")

    def importdata(self):
        """Animals that can speak are correctly identified"""
        response = self.client.post('/cc/import', { "Confirm": "Yes", "Questions":"carbon_calculator/content/Questions.csv"})
        print(response)
        #self.assertEqual(lion.speak(), 'The lion says "roar"')
        #self.assertEqual(cat.speak(), 'The cat says "meow"')
