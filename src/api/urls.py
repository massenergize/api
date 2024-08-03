from api.handlers.action import ActionHandler
from api.handlers.admin import AdminHandler
from api.handlers.auth import AuthHandler
from api.handlers.campaign import CampaignHandler
from api.handlers.campaign_account import CampaignAccountHandler
# from api.handlers.email_templates import EmailTemplatesHandler
from api.handlers.media_library import MediaLibraryHandler
from api.handlers.page_settings__aboutus import AboutUsPageSettingsHandler
from api.handlers.page_settings__actions import ActionsPageSettingsHandler
from api.handlers.page_settings__events import EventsPageSettingsHandler
from api.handlers.page_settings__vendors import VendorsPageSettingsHandler
from api.handlers.page_settings__testimonials import TestimonialsPageSettingsHandler
from api.handlers.community import CommunityHandler
from api.handlers.page_settings__contactus import ContactUsPageSettingsHandler
from api.handlers.deviceprofile import DeviceHandler
from api.handlers.page_settings__donate import DonatePageSettingsHandler
from api.handlers.page_settings__impact import ImpactPageSettingsHandler
from api.handlers.download import DownloadHandler
from api.handlers.event import EventHandler
from api.handlers.feature_flag import FeatureFlagHandler
from api.handlers.goal import GoalHandler
from api.handlers.graph import GraphHandler
from api.handlers.page_settings__home import HomePageSettingsHandler
from api.handlers.message import MessageHandler
from api.handlers.misc import MiscellaneousHandler
from api.handlers.partner import PartnerHandler
from api.handlers.policy import PolicyHandler
from api.handlers.subscriber import SubscriberHandler
from api.handlers.summary import SummaryHandler
from api.handlers.supported_language import SupportedLanguageHandler
from api.handlers.tag import TagHandler
from api.handlers.tag_collection import TagCollectionHandler
from api.handlers.task_queue import TaskQueueHandler
from api.handlers.team import TeamHandler
from api.handlers.page_settings__teams import TeamsPageSettingsHandler
from api.handlers.technology import TechnologyHandler
from api.handlers.testimonial import TestimonialHandler
from api.handlers.userprofile import UserHandler
from api.handlers.vendor import VendorHandler
from api.handlers.page_settings__register import RegisterPageSettingsHandler
from api.handlers.page_settings__signin import SigninPageSettingsHandler
from api.handlers.webhook import WebhookHandler

from django.urls import path, include



ROUTE_HANDLERS = [
    AboutUsPageSettingsHandler(),
    ActionsPageSettingsHandler(),
    ActionHandler(),
    AdminHandler(),
    AuthHandler(),
    CommunityHandler(),
    CampaignHandler(),
    CampaignAccountHandler(),
    ContactUsPageSettingsHandler(),
    DeviceHandler(),
    DonatePageSettingsHandler(),
    DownloadHandler(),
    EventHandler(),
    EventsPageSettingsHandler(),
    FeatureFlagHandler(),
    GoalHandler(),
    GraphHandler(),
    HomePageSettingsHandler(),
    ImpactPageSettingsHandler(),
    MessageHandler(),
    MiscellaneousHandler(),
    PartnerHandler(),
    PolicyHandler(),
    SubscriberHandler(),
    SummaryHandler(),
    SupportedLanguageHandler(),
    TagHandler(),
    TagCollectionHandler(),
    TeamHandler(),
    TeamsPageSettingsHandler(),
    TestimonialHandler(),
    TestimonialsPageSettingsHandler(),
    UserHandler(),
    VendorHandler(),
    VendorsPageSettingsHandler(),
    MediaLibraryHandler(),
    RegisterPageSettingsHandler(),
    SigninPageSettingsHandler(),
    TaskQueueHandler(),
    TechnologyHandler(),
    WebhookHandler()
]

urlpatterns = [
    path("cc/", include("carbon_calculator.urls")),
]
for handler in ROUTE_HANDLERS:
    urlpatterns.extend(handler.get_routes_to_views())
