# imports
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from _main_.utils.utils import Console
from api.tests.common import makeAdminGroup, makeCommunity, makeMembership, makeUser
from api.utils import filter_functions
from database.models import Role, UserProfile
from django.db import transaction
from django.test.testcases import TestCase
from database.models import Role, CommunityMember, CommunityAdminGroup
from django.db.models import Q

class FiltersFunctionTests(TestCase):
	
	def setUp(self):
		Console.header("UNIT TEST:(FiltersFunctionTests)")
		self.u1 = makeUser(email="alpha+1@gmail.com", full_name="Alpha User 1")
		self.u2 = makeUser(email="beta+2@gmail.com", full_name="Beta User 2")
		self.u3 = makeUser(email="gamma+3@gmail.com", full_name="Gamma User 3")
		self.u4 = makeUser(email="delta+4@gmail.com", full_name="Delta User 4")
		self.su = makeUser(email="su@gmail.com,", full_name="Super User", is_super_admin=True)
		self.c1 = makeCommunity(name="cAlpha")
		self.c2 = makeCommunity(name="cBeta")

		self.m1 = makeMembership(user=self.u1, community=self.c1)
		self.m2 = makeMembership(user=self.u2, community=self.c1)

		self.m3 = makeMembership(user=self.u1, community=self.c2)
		self.agm = makeAdminGroup(community=self.c1, members=[self.u4], name="TEST AGM")

	@classmethod
	def tearDownClass(self):
		super().tearDownClass() 

	def _create_roles(self):
		try:
			with transaction.atomic():
				Role.objects.bulk_create([
					Role(name=f"Test Admin-{datetime.now()}"),
					Role(name=f"Test User- {datetime.now()}"),
					Role(name=f"Test Super Admin - {datetime.now()}"),
					Role(name=f"Test Moderator- {datetime.now()}"),
					Role(name=f"Test Editor - {datetime.now()}")
				])
		except Exception:
			pass	


	def test_get_sort_params_sort_name_asc(self):
		params = {'sort_params': {'name': 'name', 'direction': 'asc'}}
		result = filter_functions.get_sort_params(params)
		self.assertEqual(result, "-name")
	
	def test_get_sort_params_sort_name_desc(self):
		params = {'sort_params': {'name': 'name', 'direction': 'desc'}}
		result = filter_functions.get_sort_params(params)
		self.assertEqual(result, "name")
	
	def test_get_sort_params_none(self):
		params = {}
		result = filter_functions.get_sort_params(params)
		self.assertEqual(result, "-created_at")
	
	# ------------------------------------------

	def test_sort_items_empty_queryset(self):
		"""
		Test sort_items function with empty queryset
		"""
		queryset = []
		params = {'sort_params': {"direction":"asc", "name":"name"}}
		result = filter_functions.sort_items(queryset, params)
		self.assertEqual(result, [])
	
	def test_sort_items_list_queryset(self):
		"""
		Test sort_items function with queryset as a list
		"""
		self._create_roles()
		qs = Role.objects.all()
		queryset = qs.order_by("-name")
		params = {'sort_params': {"direction":"asc", "name":"name"}}
		result = filter_functions.sort_items(queryset, params)
		self.assertEqual(result.first(), queryset.first(), "Result should be same as input queryset")
	
	@patch('api.utils.filter_functions.get_sort_params')
	def test_sort_items_exception_case(self, mock_get_sort_params):
		"""
		Test sort_items function where an exception occurs within the sorting action
		"""
		queryset = MagicMock()
		queryset.order_by.side_effect = Exception('Exception')
		params = {'key': 'value'}
		mock_get_sort_params.return_value = 'param1'
		result = filter_functions.sort_items(queryset, params)
		mock_get_sort_params.assert_called_once_with(params)
		queryset.order_by.assert_called_once_with('param1')
		self.assertEqual(result, queryset)

	
	@patch('api.utils.filter_functions.get_sort_params')
	def test_sort_items_returns_sorted_queryset_when_queryset_is_not_list(self, mock_get_sort_params):
		# Prepare
		mock_queryset = MagicMock()
		mock_get_sort_params.return_value = 'sort_param'
		params = {'direction': 'asc'}
		
		# Act
		result = filter_functions.sort_items(mock_queryset, params)
	
		self.assertEqual(result, mock_queryset.order_by.return_value)
		mock_get_sort_params.assert_called_once_with(params)
		mock_queryset.order_by.assert_called_once_with('sort_param')
	
	@patch('api.utils.filter_functions.get_sort_params')
	def test_sort_items_returns_queryset_when_exception_is_raised(self, mock_get_sort_params):
		# Prepare
		mock_queryset = MagicMock()
		mock_queryset.order_by.side_effect = Exception('error')
		params = {'direction': 'asc'}
		
		# Act
		result = filter_functions.sort_items(mock_queryset, params)
		
		# Assert
		self.assertEqual(result, mock_queryset)
		mock_get_sort_params.assert_called_once_with(params)



	def test_get_sort_params_sort_name_asc(self):
		params = {'sort_params': {'name': 'name', 'direction': 'asc'}}
		result = filter_functions.get_sort_params(params)
		self.assertEqual(result, "-name")
	
	def test_get_sort_params_sort_name_desc(self):
		params = {'sort_params': {'name': 'name', 'direction': 'desc'}}
		result = filter_functions.get_sort_params(params)
		self.assertEqual(result, "name")
	
	def test_get_sort_params_none(self):
		params = {}
		result = filter_functions.get_sort_params(params)
		self.assertEqual(result, "-created_at")
	
	# ------------------------------------------

	def test_sort_items_empty_queryset(self):
		"""
		Test sort_items function with empty queryset
		"""
		queryset = []
		params = {'sort_params': {"direction":"asc", "name":"name"}}
		result = filter_functions.sort_items(queryset, params)
		self.assertEqual(result, [])
	
	def test_sort_items_list_queryset(self):
		"""
		Test sort_items function with queryset as a list
		"""
		self._create_roles()
		qs = Role.objects.all()
		queryset = qs.order_by("-name")
		params = {'sort_params': {"direction":"asc", "name":"name"}}
		result = filter_functions.sort_items(queryset, params)
		self.assertEqual(result.first(), queryset.first(), "Result should be same as input queryset")
	
	@patch('api.utils.filter_functions.get_sort_params')
	def test_sort_items_exception_case(self, mock_get_sort_params):
		"""
		Test sort_items function where an exception occurs within the sorting action
		"""
		queryset = MagicMock()
		queryset.order_by.side_effect = Exception('Exception')
		params = {'key': 'value'}
		mock_get_sort_params.return_value = 'param1'
		result = filter_functions.sort_items(queryset, params)
		mock_get_sort_params.assert_called_once_with(params)
		queryset.order_by.assert_called_once_with('param1')
		self.assertEqual(result, queryset)

	
	@patch('api.utils.filter_functions.get_sort_params')
	def test_sort_items_returns_sorted_queryset_when_queryset_is_not_list(self, mock_get_sort_params):
		mock_queryset = MagicMock()
		mock_get_sort_params.return_value = 'sort_param'
		params = {'direction': 'asc'}
		
		result = filter_functions.sort_items(mock_queryset, params)
	
		self.assertEqual(result, mock_queryset.order_by.return_value)
		mock_get_sort_params.assert_called_once_with(params)
		mock_queryset.order_by.assert_called_once_with('sort_param')
	
	@patch('api.utils.filter_functions.get_sort_params')
	def test_sort_items_returns_queryset_when_exception_is_raised(self, mock_get_sort_params):
		mock_queryset = MagicMock()
		mock_queryset.order_by.side_effect = Exception('error')
		params = {'direction': 'asc'}
		
		result = filter_functions.sort_items(mock_queryset, params)
		
		self.assertEqual(result, mock_queryset)
		mock_get_sort_params.assert_called_once_with(params)


# --------------------------get_users_filter_params----------------------
	def test_get_users_filter_params_with_search(self):
		params = {'search_text': 'Beta'}
		result = filter_functions.get_users_filter_params(params)

		self.assertIsInstance(result, list)
		users = UserProfile.objects.filter(*result)
		self.assertTrue(users.exists())
		self.assertIn(self.u2, users)
		self.assertNotIn(self.u3, users)

	def test_get_users_filter_params_with_community(self):
		params = {'community': [self.c1.id]}
		result = filter_functions.get_users_filter_params(params)


		self.assertIsInstance(result, list)
		users = UserProfile.objects.filter(*result)
		
		self.assertTrue(users.exists())
		self.assertIn(self.u2, users)
		self.assertNotIn(self.u3, users)
		self.assertIn(self.u1, users)

	def test_get_users_filter_params_with_community_and_cadmin_membership(self):
		params = {'community': [self.c1.id], 'membership': ["Community Admin"]}
		result = filter_functions.get_users_filter_params(params)

		self.assertIsInstance(result, list)

		users = UserProfile.objects.filter(*result)

		self.assertTrue(users.exists())
		self.assertNotIn(self.u2, users)
		self.assertNotIn(self.u1, users)
		self.assertNotIn(self.u3, users)
		self.assertIn(self.u4, users)


	def test_get_users_filter_params_with_community_and_membership(self):
		params = {'community': [self.c1.id], 'membership': ["Member"]}
		result = filter_functions.get_users_filter_params(params)

		self.assertIsInstance(result, list)

		users = UserProfile.objects.filter(*result)

		self.assertTrue(users.exists())
		self.assertIn(self.u2, users)
		self.assertIn(self.u1, users)
		self.assertNotIn(self.u3, users)

	
	def test_get_users_filter_params_with_membership_normal(self):
		params = {'membership': ["Member"]}
		result = filter_functions.get_users_filter_params(params)

		self.assertIsInstance(result, list)

		users = UserProfile.objects.filter(*result)
		self.assertTrue(users.exists())
		self.assertIn(self.u2, users)
		self.assertIn(self.u1, users)
		self.assertIn(self.u3, users)

	def test_get_users_filter_params_with_membership_su(self):
		params = params = {'membership': ["Super Admin"]}
		result = filter_functions.get_users_filter_params(params)

		self.assertIsInstance(result, list)

		users = UserProfile.objects.filter(*result)
		self.assertTrue(users.exists())
		self.assertNotIn(self.u2, users)
		self.assertNotIn(self.u1, users)
		self.assertNotIn(self.u3, users)
		self.assertIn(self.su, users)
		



if __name__ == "__main__":
	unittest.main()
