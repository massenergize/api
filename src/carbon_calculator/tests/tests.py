from django.test import TestCase, Client
from carbon_calculator.models import CalcUser, Event, Station, Action, Group, Question
from carbon_calculator.views import importcsv
from database.models import Vendor
from django.db.models import Count
import jsons
import requests

IMPORT_SUCCESS = {"status": True}


# Create your tests here.
class CarbonCalculatorTest(TestCase):
    @classmethod
    def setUpClass(self):
        ''' This will run before any tests occur. This is loading the files that are associated with the various
            carbon calculator models. '''

        self.client = Client()  # this will act as fake user, so it will send urls to the server for testing
        self.client.post('/cc/import',
                         {"Confirm": "Yes",
                          "Actions": "carbon_calculator/content/Actions.csv",
                          "Questions": "carbon_calculator/content/Questions.csv",
                          "Stations": "carbon_calculator/content/Stations.csv",
                          "Groups": "carbon_calculator/content/Groups.csv",
                          "Events": "carbon_calculator/content/Events.csv",
                          "Defaults": "carbon_calculator/content/exportdefaults.csv"
                          })

    @classmethod
    def tearDownClass(self):
        ''' this i think will run after the setup class... not really sure... might run after all of the tests... '''
        populate_inputs_file()

    def test_info_actions(self):
        ''' Makes sure path to /cc/info/actions is successful '''

        response = self.client.post('/cc/info/actions')
        self.assertEqual(response.status_code, 200)    # remember status code 200 is a good status

    def test_solarPVNoArgs(self):
        ''' Ya so kinda confused with this whole class... cause I've tried to type out that url and I get a error
            but when i do a assert equal for a good status code I get no errors... weird... '''
        # why is this response good? Becuase when I type it in it won't work
        response = self.client.post('/cc/getInputs/install_solarPV', {})
        data = jsons.loads(response.content)
        # outputInputs(data)

    def test_solarPVGreat(self):
        ''' gotta by honest don't really know to much about this. I just know this is greg and josh's thing so
            imma just leave at that... '''
        response = self.client.post('/cc/getInputs/install_solarPV',
                                    {
                                        'solar_potential': 'Great'
                                    }
                                    )
        data = jsons.loads(response.content)
        # print('solarPV data: \n')
        # print(data)

    def test_led_number_nonefficient_bulbs(self):
        response = self.client.post('/cc/getInputs/led_lighting',
                                    {
                                        'bulbs_incandescent': 'Less than 10'
                                    }
                                    )
        #data = jsons.loads(response.content)
        #print(data)
        #print(response)
        # #print('led_lighting data: \n')

    # 1 !!!!!!! Works !!!!!!!
    def test_info_events(self):
        ''' Tests /cc/info/events url and returns a json of events. '''

        event_list = self.client.get("/cc/info/events", {}) # status code = 200
        event_list_json = jsons.loads(event_list.content)   # loads into json
        #print(event_list_json)                             # uncomment this to see json

    # 2 I belive this one works... little unsure
    def test_info_all_events(self):
        '''tests /cc/info/event/~eventName~ and should return all data about that event '''
        #print("2")
        obj = Event.objects.first()  # getting the first object in model
        field_object = Event._meta.get_field('name') # this and next is getting the name
        #print("field object")
        #print(field_object)
        field_value = field_object.value_from_object(obj) # this returns actual name (as str)
        #print("field value")
        #print(field_value)

        # UPDATE WORKS !!! Well pretty sure, gives me all of the info sooooo
        event_url = "/cc/info/event/" + field_value
        #print(event_url)
        event_info = self.client.get(event_url, {})
        event_json = jsons.loads(event_info.content)
        #print(event_json)

    # 4 !!!!!!! WORKS !!!!!!!
    def test_info_impact_event(self):
        #print("test info impact event")
        obj = Event.objects.first()  # getting the first object in model
        field_object = Event._meta.get_field('name')  # this and next is getting the name
        field_value = field_object.value_from_object(obj)  # this returns actual name (as str)
        #print(field_value)

        event_url = "/cc/info/impact/" + field_value
        #print(event_url)
        event_info = self.client.get(event_url, {})
        event_json = jsons.loads(event_info.content)
        #print(event_json)

    # 6 !!!!!!! WORKS !!!!!!!
    def test_info_on_one_group(self):
        obj = Group.objects.first()
        field_object = Group._meta.get_field('name')
        field_value = field_object.value_from_object(obj)
        #print(field_value)

        event_url = "/cc/info/group/" + field_value
        #print(event_url)
        event_info = self.client.get(event_url, {})
        event_json = jsons.loads(event_info.content)
        #print(event_json)

    # 8 !!!!!!! WORKS !!!!!!!
    def test_info_stations_one_station(self):
        obj = Station.objects.first()
        field_object = Station._meta.get_field('name')
        field_value = field_object.value_from_object(obj)
        #print(field_value)

        event_url = "/cc/info/station/" + field_value
        #print(event_url)
        event_info = self.client.get(event_url, {})
        event_json = jsons.loads(event_info.content)
        #print(event_json)

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
        #print(field_value)

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

# don't care about this rn...
def outputInputs(data):
    f = open("carbon_calculator/tests/Inputs.txt", "a")
    f.write(str(data) + "\n")
    f.close()
#don't care about this rn...
def populate_inputs_file():
    client = Client()
    response = client.get("/cc/info/actions")
    data = jsons.loads(response.content)["actions"]
    # print(data)
    names = [i["name"] for i in data]
    # print(names)
    for name in names:
        try:
            outputInputs(
                jsons.loads(
                    client.post(
                        "/cc/getInputs/{}".format(name), {}
                    ).content
                )
            )
        except:
            pass


"""Results from run with above settings:
Inputs to EvalSolarPV: {'solar_potential': 'Great'}
{'status': 0, 'carbon_points': 5251.0, 'cost': 14130.0, 'savings': 3241.0, 'explanation': 'installing a solar PV array on your home would pay back in around 5 years and save 26.3 tons of CO2 over 10 years.'}
.    """
