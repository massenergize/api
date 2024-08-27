""" 
    Miscellaneous routes: store layer
"""
from _main_.utils.footage.spy import Spy
from api.tests.common import createUsers
from database.models import (
    Action,
    Vendor,
    Event,
    Menu,
    UserProfile,
    HomePageSettings,
)
    Community,
from _main_.utils.massenergize_errors import (
    CustomMassenergizeError,
    InvalidResourceError,
    MassEnergizeAPIError,
)
from _main_.utils.context import Context
from database.models import CarbonEquivalency
from .utils import get_community
from typing import Tuple
from api.utils.api_utils import get_viable_menu_items
from _main_.utils.utils import load_json
from api.tests.common import createUsers
from api.utils.api_utils import load_default_menus_from_json, \
    remove_unpublished_menu_items, validate_menu_content
from database.utils.common import json_loader
from .utils import check_location, find_reu_community, get_community, split_location_string
from ..constants import MENU_CONTROL_FEATURE_FLAGS


def remove_menu_links_based_on_feature_flag(links, community):
    links_to_hide = []
    values = MENU_CONTROL_FEATURE_FLAGS.values()
    feature_flags = FeatureFlag.objects.filter(key__in=values)
    for link, feature_flag_key in MENU_CONTROL_FEATURE_FLAGS.items():
        db_feature_flag = feature_flags.filter(key=feature_flag_key).first()
        if not db_feature_flag or not db_feature_flag.is_enabled_for_community(community):
            links_to_hide.append(link)
    return remove_unpublished_menu_items(links, links_to_hide)


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
            log.exception(e)
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
            log.exception(e)
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
            log.exception(e)
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
            
            menus = Menu.objects.filter(community=community, is_published=True)
            if not menus:
                return None, CustomMassenergizeError("No menus found for this community")
            
            menu = menus.first()
            
            portal_main_nav_links = remove_menu_links_based_on_feature_flag(menu.content, community)
            portal_footer_quick_links = remove_menu_links_based_on_feature_flag(menu.footer_content.get("links", []), community)
            
            return [
                {"name": "PortalMainNavLinks", "content": portal_main_nav_links},
                {"name": "PortalFooterQuickLinks", "content": {"links": portal_footer_quick_links}},
                menu.contact_info
            
            ], None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
        
    def create_menu(self, context, args):
        try:
            community_id = args.pop('community_id', None)
            subdomain = args.pop('subdomain', None)
            
            if not community_id and not subdomain:
                return None, CustomMassenergizeError("community_id or subdomain not provided")
            
            community, error = get_community(community_id=community_id, subdomain=subdomain)
            
            if error:
                return None, error
            
            default_menus = load_default_menus_from_json()
            
            name = f"{community.subdomain} Main Menu"
            args["name"] = name
            args["community"] = community
            args["is_custom"] = True
            args["content"] = default_menus["PortalMainNavLinks"]
            args["footer_content"] = default_menus["PortalFooterQuickLinks"]
            args["contact_info"] = default_menus["PortalFooterContactInfo"]
            
            menu = Menu.objects.create(**args)
            
            return menu, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def update_menu(self, context, args):
        try:
            menu_id = args.pop('id', None)
            content = args.pop('content', None)
            footer_content = args.pop('footer_content', None)
            contact_info = args.pop('contact_info', None)
            
            if not menu_id:
                return None, CustomMassenergizeError("id not provided")
            
            community_logo_id = args.pop('community_logo_id', None)
            
            menu = Menu.objects.filter(id=menu_id)
            
            if not menu:
                return None, CustomMassenergizeError("Menu not found")
            
            args["is_custom"] = True
            
            menu.update(**args)
            
            if content:
            
                is_content_valid = validate_menu_content(content)
                
                if not is_content_valid:
                    return None, CustomMassenergizeError("Invalid menu content")
                menu.update(content=content)

            if footer_content:
                is_footer_content_valid = validate_menu_content(footer_content.get('links', []))
                
                if not is_footer_content_valid:
                    return None, CustomMassenergizeError("Invalid footer content")
                
                menu.update(footer_content=footer_content)
                
            if contact_info:
                menu.update(contact_info=contact_info)
                
            if community_logo_id:
                community = menu.first().community
                community.logo = Media.objects.get(id=community_logo_id)
                community.save()

            return menu.first(), None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
            
    def delete_menu(self, context, args):
        try:
            menu_id = args.pop('id', None)
            menu = Menu.objects.filter(id=menu_id)
            
            if not menu:
                return None, CustomMassenergizeError("Menu not found")
            
            menu = menu.first()
            if not menu.is_custom:
                return None, CustomMassenergizeError("Cannot delete default menu. Try resetting it instead")
            
            menu.delete()
            return True, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
        
    def get_menu(self, context, args):
        try:
            menu_id = args.pop('id', None)
            menu = Menu.objects.filter(id=menu_id)
            
            if not menu:
                return None, CustomMassenergizeError("Menu not found")
                
            return menu.first(), None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def get_menus_for_admin(self, context, args):
        try:
            community_id = args.pop('community_id', None)
            subdomain = args.pop('subdomain', None)
            
            if not community_id and not subdomain:
                return None, CustomMassenergizeError("community_id or subdomain not provided")
            
            community, error = get_community(community_id=community_id, subdomain=subdomain)
            
            if error:
                return None, error
            
            menus = Menu.objects.filter(community=community)
            
            for menu in menus:
                menu.content = remove_menu_links_based_on_feature_flag(menu.content, community)
                menu.footer_content = remove_menu_links_based_on_feature_flag(menu.footer_content.get("links", []), community)
            
            return menus, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
        
    def reset_menu(self, context, args):
        try:
            menu_id = args.pop('id', None)
            
            if not menu_id:
                return None, CustomMassenergizeError("id not provided!!")
            
            menu = Menu.objects.filter(id=menu_id)
            
            if not menu:
                return None, CustomMassenergizeError("Menu not found")
            
            menu = menu.first()
            
            default_menus = load_default_menus_from_json()
            
            menu.content = default_menus["PortalMainNavLinks"]
            # menu.footer_content = default_menus["PortalFooterQuickLinks"]
            # menu.contact_info = default_menus["PortalFooterContactInfo"]
            menu.is_custom = False
            menu.save()
            
            return menu, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
        
        
    def list_all_languages(self, context, args) -> (dict, Exception):
        """ Get all the languages """
        try:
            all_languages = load_json("database/raw_data/other/languages.json")
            return all_languages, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))
