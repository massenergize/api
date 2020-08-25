from api.handlers.action import ActionHandler
from api.handlers.admin import AdminHandler
from api.handlers.auth import AuthHandler
from api.handlers.page_settings__aboutus import AboutUsPageSettingsHandler
from api.handlers.page_settings__actions import ActionsPageSettingsHandler
from api.handlers.community import CommunityHandler
from api.handlers.page_settings__contactus import ContactUsPageSettingsHandler
from api.handlers.page_settings__donate import DonatePageSettingsHandler
from api.handlers.download import DownloadHandler
from api.handlers.event import EventHandler
from api.handlers.goal import GoalHandler
from api.handlers.graph import GraphHandler
from api.handlers.page_settings__home import HomePageSettingsHandler
from api.handlers.message import MessageHandler
from api.handlers.misc import MiscellaneousHandler
from api.handlers.policy import PolicyHandler
from api.handlers.subscriber import SubscriberHandler
from api.handlers.summary import SummaryHandler
from api.handlers.tag import TagHandler
from api.handlers.tag_collection import TagCollectionHandler
from api.handlers.team import TeamHandler
from api.handlers.page_settings__teams import TeamsPageSettingsHandler
from api.handlers.testimonial import TestimonialHandler
from api.handlers.userprofile import UserHandler
from api.handlers.vendor import VendorHandler


ROUTE_HANDLERS = [
  AboutUsPageSettingsHandler(),
  ActionsPageSettingsHandler(),
  ActionHandler(),
  AdminHandler(),
  AuthHandler(),
  CommunityHandler(),
  ContactUsPageSettingsHandler(),
  DownloadHandler(), 
  DonatePageSettingsHandler(),
  EventHandler(),
  GoalHandler(),
  GraphHandler(),
  HomePageSettingsHandler(),
  MessageHandler(),
  MiscellaneousHandler(),
  PolicyHandler(),
  SubscriberHandler(),
  SummaryHandler(),
  TagHandler(),
  TagCollectionHandler(),
  TeamHandler(),
  TeamsPageSettingsHandler(),
  TestimonialHandler(),
  UserHandler(),
  VendorHandler()
]

urlpatterns = []
for handler in ROUTE_HANDLERS:
  urlpatterns.extend(handler.get_routes_to_views())


