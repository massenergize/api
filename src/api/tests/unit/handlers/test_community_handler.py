import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from _main_.utils.feature_flag_keys import USER_EVENTS_NUDGES_FF
from api.handlers.community import CommunityHandler
from _main_.utils.utils import Console
from _main_.utils.massenergize_response import MassenergizeResponse
from api.tests.common import makeCommunity
from database.models import Community, CommunityNotificationSetting


class TestCommunityHandler(unittest.TestCase):
	def setUp(self):
		self.instance = CommunityHandler()
		self.request = Mock()
		self.community = makeCommunity()
		self.setting = CommunityNotificationSetting.objects.create(community=self.community, is_active=False, notification_type=USER_EVENTS_NUDGES_FF)
	
	@patch("api.handlers.community.CommunityHandler.validator", create=True)
	@patch("api.handlers.community.CommunityHandler.service", create=True)
	def test_list_community_notification_settings(self, mock_service, mock_validator):
		Console.header("UNIT TEST:(handler) list_community_notification_settings")
		self.request.context = Mock()
		self.request.context.args = {"community_id": self.community.id}
		
		mock_validator.verify.return_value = (self.request.context.args, None)
		mock_service.list_community_notification_settings.return_value = ([], None)
		
		response = self.instance.list_community_notification_settings(self.request)
	
		self.assertIsInstance(response, MassenergizeResponse)

	@patch("api.handlers.community.CommunityHandler.validator", create=True)
	@patch("api.handlers.community.CommunityHandler.service", create=True)
	def test_update_community_notification_settings_unit(self, mock_service, mock_validator):
		Console.header("UNIT TEST:(handler) update_community_notification_settings")
		
		today = datetime.now().date()
		
		request = Mock()
		request.context = Mock()
		
		request.context.args = {"id": self.setting.id, "is_active": True, "activate_on": today}
		
		mock_validator.verify.return_value = (request.context.args, None)
		mock_service.update_community_notification_settings.return_value = (True, None)
		
		response = self.instance.update_community_notification_settings(request)
		self.assertIsInstance(response, MassenergizeResponse)
		
	@patch("api.handlers.community.CommunityHandler.validator", create=True)
	@patch("api.handlers.community.CommunityHandler.service", create=True)
	def test_request_feature_for_community_unit(self, mock_service, mock_validator):
		Console.header("UNIT TEST:(handler) request_feature_for_community")
		
		request = Mock()
		request.context = Mock()
		
		request.context.args = {"community_id": self.community.id, "feature_flag_key": USER_EVENTS_NUDGES_FF, "enable": True}
		
		mock_validator.verify.return_value = (request.context.args, None)
		mock_service.update_community_notification_settings.return_value = (True, None)
		
		response = self.instance.update_community_notification_settings(request)
		self.assertIsInstance(response, MassenergizeResponse)
	
