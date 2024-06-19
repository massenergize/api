"""
This is the test file for device profiles
"""
from django.test import  TestCase, Client
from six import print_
from database.models import DeviceProfile
from database.models import DeviceProfile
from urllib.parse import urlencode
from api.tests.common import signinAs, createUsers

class DeviceHandlerTest(TestCase):

    @classmethod
    def setUpClass(self):
      
      print("\n---> Testing Devices <---\n")

      self.client = Client()
      
      self.USER, self.CADMIN, self.SADMIN = createUsers()
    
      signinAs(self.client, self.SADMIN)

      signinAs(self.client, None)

      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      devices = DeviceProfile.objects.filter(id=create_response["data"]["id"])
      self.device = devices.first()

      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      devices = DeviceProfile.objects.filter(id=create_response["data"]["id"])
      self.device1 = devices.first()

      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      devices = DeviceProfile.objects.filter(id=create_response["data"]["id"])
      self.device2 = devices.first()

      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      devices = DeviceProfile.objects.filter(id=create_response["data"]["id"])
      self.device3 = devices.first()


    @classmethod
    def tearDownClass(self):
      pass

    def setUp(self):
      # this gets run on every test case
      pass

    def test_create(self):
      # test create not logged in
      signinAs(self.client, None)
      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": create_response["data"]["id"]}), content_type="application/x-www-form-urlencoded").toDict()

      # test create logged as user
      signinAs(self.client, self.USER)
      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": create_response["data"]["id"]}), content_type="application/x-www-form-urlencoded").toDict()

      # test create logged as cadmin
      signinAs(self.client, self.CADMIN)
      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": create_response["data"]["id"]}), content_type="application/x-www-form-urlencoded").toDict()

      # test create logged as sadmin
      signinAs(self.client, self.SADMIN)
      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": create_response["data"]["id"]}), content_type="application/x-www-form-urlencoded").toDict()
    
    def test_info(self):

      # test info not logged in
      signinAs(self.client, None)
      info_response = self.client.post('/api/device.info', urlencode({"id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as user
      signinAs(self.client, self.USER)
      info_response = self.client.post('/api/device.info', urlencode({"id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as cadmin
      signinAs(self.client, self.CADMIN)
      info_response = self.client.post('/api/device.info', urlencode({"id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as sadmin
      signinAs(self.client, self.SADMIN)
      info_response = self.client.post('/api/device.info', urlencode({"id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

    # def test_update(self): # Currently update does nothing since data is grabbed from the back end
    #   # test update not signed in
    #   signinAs(self.client, None)
    #   update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
    #   self.assertTrue(update_response["success"])
    #   
    #   # test update signed as user
    #   signinAs(self.client, self.USER)
    #   update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
    #   self.assertTrue(update_response["success"])
    #   
    #   # test update as cadmin
    #   signinAs(self.client, self.CADMIN)
    #   update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
    #   self.assertTrue(update_response["success"])
    #   self.assertEquals(update_response["data"]["title"], "cadmin_title")
    #   
    #   # test update as sadmin
    #   signinAs(self.client, self.SADMIN)
    #   update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
    #   self.assertTrue(update_response["success"])
    #   self.assertEquals(update_response["data"]["title"], "sadmin_title")
    
    def test_device_log(self):
      visit_log = self.device.visit_log
      visit_logs = len(visit_log)

      # test update not signed in
      signinAs(self.client, None)
      log_response = self.client.post('/api/device.log', urlencode({"device_id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
      visit_logs += 1
      self.assertTrue(log_response["success"])
      # self.assertEquals(len(log_response["data"]["visit_log"]), visit_logs)
    
    def test_user_log(self):
      visit_log = self.device1.visit_log
      visit_logs = len(visit_log)

      # test log signed as user
      signinAs(self.client, self.USER)
      log_response = self.client.post('/api/device.log', urlencode({"device_id": self.device1.id}), content_type="application/x-www-form-urlencoded").toDict()
      visit_logs += 1
      self.assertTrue(log_response["success"])
      # self.assertEquals(len(log_response["data"]["visit_log"]), visit_logs)

      visit_log = self.device2.visit_log
      visit_logs = len(visit_log)

      # test log as cadmin
      signinAs(self.client, self.CADMIN)
      log_response = self.client.post('/api/device.log', urlencode({"device_id": self.device2.id}), content_type="application/x-www-form-urlencoded").toDict()
      visit_logs += 1
      self.assertTrue(log_response["success"])
      # self.assertEquals(len(log_response["data"]["visit_log"]), visit_logs)

      visit_log = self.device3.visit_log
      visit_logs = len(visit_log)

      # test log as sadmin
      signinAs(self.client, self.SADMIN)
      log_response = self.client.post('/api/device.log', urlencode({"device_id": self.device3.id}), content_type="application/x-www-form-urlencoded").toDict()
      visit_logs += 1
      self.assertTrue(log_response["success"])
      # self.assertEquals(len(log_response["data"]["visit_log"]), visit_logs)

    # device object has no attribute first?
    def test_delete(self):
      # test not signed in
      signinAs(self.client, None)
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": self.device.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(delete_response["success"])
      self.assertTrue(delete_response["data"]["is_deleted"])

      # test as user
      signinAs(self.client, self.USER)
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": self.device1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(delete_response["success"])
      self.assertTrue(delete_response["data"]["is_deleted"])

      # test as cadmin
      signinAs(self.client, self.CADMIN)
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": self.device2.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(delete_response["success"])
      self.assertTrue(delete_response["data"]["is_deleted"])

      # test as sadmin
      signinAs(self.client, self.SADMIN)
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": self.device3.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(delete_response["success"])
      self.assertTrue(delete_response["data"]["is_deleted"])

      # test no device_id
      delete_response = self.client.post('/api/device.delete', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(delete_response["success"])    
