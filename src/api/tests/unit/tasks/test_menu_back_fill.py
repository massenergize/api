from django.test import TestCase

from api.tests.common import makeCommunity
from task_queue.database_tasks.menu_backfill import back_fill_menu


class BackFillMenuTest(TestCase):
	def setUp(self):
		makeCommunity()
		makeCommunity()
	
	def tearDown(self):
		pass
	
	def test_back_fill_menu(self):
		print("\n\n\nTEST: test_back_fill_menu")
		result = back_fill_menu()
		self.assertTrue(result.get("success"))
		self.assertIsNone(result.get("error"))

