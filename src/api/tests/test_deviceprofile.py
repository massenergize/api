"""
This is the test file for device profiles
"""
from django.test import  TestCase, Client
from api.src.database.models import DeviceProfile
from database.models import DeviceProfile, Community, CommunityAdminGroup
import json
from urllib.parse import urlencode
from api.tests.common import signinAs, setupCC, createUsers

class DeviceHandlerTest(TestCase):

    @classmethod
    def setUpClass(self):
      
      print("\n---> Testing Devices <---\n")

      self.client = Client()
      
      self.USER, self.CADMIN, self.SADMIN = createUsers()
    
      signinAs(self.client, self.SADMIN)

      setupCC(self.client)


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

      # test create logged as user
      signinAs(self.client, self.USER)
      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])

      # test create logged as cadmin
      signinAs(self.client, self.CADMIN)
      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])

      # test create logged as sadmin
      signinAs(self.client, self.SADMIN)
      create_response = self.client.post('/api/device.create', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(create_response["success"])
    
    def test_info(self):
      # test info not logged in
      signinAs(self.client, None)
      info_response = self.client.post('/api/device.info', urlencode({"id": self.device1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as user
      signinAs(self.client, self.USER)
      info_response = self.client.post('/api/device.info', urlencode({"id": self.device1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as cadmin
      signinAs(self.client, self.CADMIN)
      info_response = self.client.post('/api/device.info', urlencode({"id": self.device1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

      # test info logged as sadmin
      signinAs(self.client, self.SADMIN)
      info_response = self.client.post('/api/device.info', urlencode({"id": self.device1.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(info_response["success"])

    def test_update(self):
      # test update not signed in
      signinAs(self.client, None)
      update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device1.id, "title": "none_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(update_response["success"])

      # test update signed as user
      signinAs(self.client, self.USER)
      update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device1.id, "title": "user_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(update_response["success"])

      # test update as cadmin
      signinAs(self.client, self.CADMIN)
      update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device1.id, "title": "cadmin_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(update_response["success"])
      self.assertEquals(update_response["data"]["title"], "cadmin_title")

      # test update as sadmin
      signinAs(self.client, self.SADMIN)
      update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device1.id, "title": "sadmin_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(update_response["success"])
      self.assertEquals(update_response["data"]["title"], "sadmin_title")
    
    def test_log(self):
      # test update not signed in
      signinAs(self.client, None)
      update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device1.id, "title": "none_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(update_response["success"])

      # test update signed as user
      signinAs(self.client, self.USER)
      update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device1.id, "title": "user_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(update_response["success"])

      # test update as cadmin
      signinAs(self.client, self.CADMIN)
      update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device1.id, "title": "cadmin_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(update_response["success"])
      self.assertEquals(update_response["data"]["title"], "cadmin_title")

      # test update as sadmin
      signinAs(self.client, self.SADMIN)
      update_response = self.client.post('/api/device.update', urlencode({"device_id": self.device1.id, "title": "sadmin_title"}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(update_response["success"])
      self.assertEquals(update_response["data"]["title"], "sadmin_title")

    # device object has no attribute first?
    def test_delete(self):
      # test not signed in
      signinAs(self.client, None)
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": self.device3.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(delete_response["success"])

      # test as user
      signinAs(self.client, self.USER)
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": self.device3.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(delete_response["success"])

      # test as cadmin
      signinAs(self.client, self.CADMIN)
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": self.device4.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(delete_response["success"])
      self.assertTrue(delete_response["data"]["is_deleted"])

      # test as sadmin
      signinAs(self.client, self.SADMIN)
      delete_response = self.client.post('/api/device.delete', urlencode({"device_id": self.device5.id}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertTrue(delete_response["success"])
      self.assertTrue(delete_response["data"]["is_deleted"])

      # test no device_id
      delete_response = self.client.post('/api/device.delete', urlencode({}), content_type="application/x-www-form-urlencoded").toDict()
      self.assertFalse(delete_response["success"])    
