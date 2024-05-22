""" 
    Miscellaneous routes: store layer
"""
from _main_.utils.footage.spy import Spy
from api.tests.common import createUsers
from database.models import (
    Action,
    Vendor,
    Event,
    Community,
    Menu,
    UserProfile,
    HomePageSettings,
)
from _main_.utils.massenergize_errors import (
    CustomMassenergizeError,
    InvalidResourceError,
    MassEnergizeAPIError,
)
from _main_.utils.context import Context
from database.models import CarbonEquivalency
from .utils import get_community
from sentry_sdk import capture_message
from typing import Tuple
from api.utils.api_utils import get_viable_menu_items


class MiscellaneousStore:
    def __init__(self):
        self.name = "Miscellaneous Store/DB"
        #self.list_commonly_used_icons()

    def fetch_footages(self,context:Context, args): 
        footages = None 
        try:
            if context.user_is_super_admin: 
                footages = Spy.fetch_footages_for_super_admins(context = context)
            else: 
                footages = Spy.fetch_footages_for_community_admins(context = context)

            return footages, None
        except Exception as e: 
            return None, str(e)


    def authenticateFrontendInTestMode(self, args): 
        email = args.get("email"); 
        user = UserProfile.objects.filter(email = email).first() 
        if not user: 
            user = createUsers(email = email, full_name = "Master Chef - Test")
        return user, None
        
    def remake_navigation_menu(self, json) -> Tuple[dict, MassEnergizeAPIError]:
        Menu.objects.all().delete()
        for name, menu in json.items():
            new_menu = Menu(name=name, content=menu)
            try:
                new_menu.save()
            except:
                return {}, "Sorry, could not remake menu"
        return json or {}, None

    def navigation_menu_list(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            main_menu = Menu.objects.all()
            return main_menu, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def actions_report(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        print("Actions report!")
        total = 0
        total_wo_ccaction = 0
        for c in Community.objects.filter(is_published=True):
            print(c)
            actions = Action.objects.filter(community__id=c.id, is_published=True, is_deleted=False)
            total += actions.count()
            for action in actions:
                if action.calculator_action == None:
                    total_wo_ccaction += 1
                    print(action.title + " has no corresponding CCAction")
        print("Total actions = "+str(total) + ", no CCAction ="+str(total_wo_ccaction))
        return None, None


    def create_carbon_equivalency(self, args):
        try:
            new_carbon_equivalency = CarbonEquivalency.objects.create(**args)
            return new_carbon_equivalency, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_carbon_equivalency(self, args):
        try:
            id = args.get("id", None)

            carbon_equivalencies = CarbonEquivalency.objects.filter(id=id)

            if not carbon_equivalencies:
                return None, InvalidResourceError()

            carbon_equivalencies.update(**args)
            carbon_equivalency = carbon_equivalencies.first()

            return carbon_equivalency, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def get_carbon_equivalencies(self, args):

        id = args.get("id", None)
        if id:
            carbon_equivalencies = CarbonEquivalency.objects.filter(id=id)
            if not carbon_equivalencies:
                return None, InvalidResourceError()
            else:
                carbon_equivalencies = carbon_equivalencies.first()

        else:
            carbon_equivalencies = CarbonEquivalency.objects.all()
        return carbon_equivalencies, None

    def delete_carbon_equivalency(self, args):
        id = args.get("id", None)
        carbon_equivalency = CarbonEquivalency.objects.filter(id=id)

        if not carbon_equivalency:
            return None, InvalidResourceError()

        carbon_equivalency.delete()
        return carbon_equivalency, None

    def generate_sitemap_for_portal(self):
        return {
            "communities": Community.objects.filter(
                is_deleted=False, is_published=True
            ).values("id", "subdomain", "updated_at"),
            "actions": Action.objects.filter(
                is_deleted=False,
                is_published=True,
                community__is_published=True,
                community__is_deleted=False,
            )
            .select_related("community")
            .values("id", "community__subdomain", "updated_at"),
            "services": Vendor.objects.filter(is_deleted=False, is_published=True)
            .prefetch_related("communities")
            .values("id", "communities__subdomain", "updated_at"),
            "events": Event.objects.filter(
                is_deleted=False,
                is_published=True,
                community__is_published=True,
                community__is_deleted=False,
            )
            .select_related("community")
            .values("id", "community__subdomain"),
        }

    # utility routine to list icons from the database
    def list_commonly_used_icons(self):

        common_icons = {}
        #action.icon
        #button.icon
        #service.icon
        #card.icon
        #tag.icon
        #CarbonEquivalency.icon

        #HomePageSettings.featured_links json
        all_hps = HomePageSettings.objects.all()
        for hps in all_hps:
            if hps.featured_links:
                for item in hps.featured_links:
                    icon = item["icon"]
                    if icon in common_icons.keys():
                        common_icons[icon] += 1
                    else:
                        common_icons[icon] = 1

        sorted_keys = sorted(common_icons, key=common_icons.get, reverse=True)
        for key in sorted_keys:
            print(str(key) + ": " + str(common_icons[key]))

    def load_menu_items(self, context, args):
        try:
            subdomain = args.get("subdomain", None)
            community_id = args.get("community_id", None)

            if not subdomain and not community_id:
                return None, CustomMassenergizeError("No community or subdomain provided")

            community, _ = get_community(community_id=community_id, subdomain=subdomain)
            if not community:
                return None, CustomMassenergizeError("Community not found")

            menu = get_viable_menu_items(community)

            return menu, None
        except Exception as e:
            return None, CustomMassenergizeError(e)