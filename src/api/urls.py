from django.urls import path, re_path
from django.conf.urls import url
from .views import *

from api.handlers.action import ActionHandler
from api.handlers.admin import AdminHandler
from api.handlers.community import CommunityHandler
from api.handlers.event import EventHandler
from api.handlers.goal import GoalHandler
from api.handlers.graph import GraphHandler
from api.handlers.page_settings__aboutus import AboutUsPageSettingsHandler
from api.handlers.page_settings__actions import ActionsPageSettingsHandler
from api.handlers.page_settings__contactus import ContactUsPageSettingsHandler
from api.handlers.page_settings__donate import DonatePageSettingsHandler
from api.handlers.page_settings__home import HomePageSettingsHandler
from api.handlers.message import MessageHandler
from api.handlers.misc import MiscellaneousHandler
from api.handlers.policy import PolicyHandler
from api.handlers.subscriber import SubscriberHandler
from api.handlers.summary import SummaryHandler
from api.handlers.tag import TagHandler
from api.handlers.tag_collection import TagCollectionHandler
from api.handlers.team import TeamHandler
from api.handlers.testimonial import TestimonialHandler
from api.handlers.userprofile import UserHandler
from api.handlers.vendor import VendorHandler





urlpatterns = []
urlpatterns.extend(AboutUsPageSettingsHandler().get_routes_to_views())
urlpatterns.extend(ActionHandler().get_routes_to_views())
urlpatterns.extend(ActionsPageSettingsHandler().get_routes_to_views())
urlpatterns.extend(AdminHandler().get_routes_to_views())
urlpatterns.extend(CommunityHandler().get_routes_to_views())
urlpatterns.extend(ContactUsPageSettingsHandler().get_routes_to_views())
urlpatterns.extend(DonatePageSettingsHandler().get_routes_to_views())
urlpatterns.extend(EventHandler().get_routes_to_views())
urlpatterns.extend(GoalHandler().get_routes_to_views())
urlpatterns.extend(GraphHandler().get_routes_to_views())
urlpatterns.extend(MessageHandler().get_routes_to_views())
urlpatterns.extend(MiscellaneousHandler().get_routes_to_views())
urlpatterns.extend(PolicyHandler().get_routes_to_views())
urlpatterns.extend(SubscriberHandler().get_routes_to_views())
urlpatterns.extend(SummaryHandler().get_routes_to_views())
urlpatterns.extend(HomePageSettingsHandler().get_routes_to_views())
urlpatterns.extend(TagHandler().get_routes_to_views())
urlpatterns.extend(TagCollectionHandler().get_routes_to_views())
urlpatterns.extend(TeamHandler().get_routes_to_views())
urlpatterns.extend(TestimonialHandler().get_routes_to_views())
urlpatterns.extend(UserHandler().get_routes_to_views())
urlpatterns.extend(VendorHandler().get_routes_to_views())

