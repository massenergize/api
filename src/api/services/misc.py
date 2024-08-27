import logging

from django.test import Client
from _main_.utils.constants import INSPIRATIONAL_MESSAGES
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
    CustomMassenergizeError,
)
from _main_.utils.common import serialize, serialize_all
from api.store.misc import MiscellaneousStore
from _main_.utils.context import Context
from django.shortcuts import render
from api.tests.common import signinAs
from api.utils.api_utils import get_list_of_internal_links
from database.models import Deployment
from _main_.settings import IS_PROD, IS_CANARY, BASE_DIR, EnvConfig, TEST_PASSPORT_KEY
from _main_.utils.utils import load_json, load_text_contents
from django.db.models.query import QuerySet
from typing import Tuple
import random

# PASSPORT_KEY = os.environ.get("TEST_PASSPORT_KEY")
class MiscellaneousService:
    """
    Service Layer for all the goals
    """

    def __init__(self):
        self.store = MiscellaneousStore()

    def fetch_footages(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        footages, error = self.store.fetch_footages(context, args)
        if error:
            return None, error
        count = footages.count()
        return {
            "count":count,
            "footages": serialize_all(footages),
            "activityTypes": FootageConstants.TYPES,
            "types": FootageConstants.ITEM_TYPES,
            "platforms": FootageConstants.PLATFORMS,
        }, None

    def remake_navigation_menu(self) -> Tuple[dict, MassEnergizeAPIError]:
        json = load_json(BASE_DIR + "/database/raw_data/portal/menu.json")
        return self.store.remake_navigation_menu(json)

    def navigation_menu_list(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        main_menu_items, err = self.store.navigation_menu_list(context, args)
        if err:
            return None, err
        return serialize_all(main_menu_items), None

    def actions_report(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        result, err = self.store.actions_report(context, args)
        if err:
            return None, err
        return result, None

    def home(self, ctx: Context, request):
        release_info = EnvConfig.release_info or {}
        SITE_TITLE = f"MassEnergize-API-{EnvConfig.name}"

        if IS_PROD:
            SITE_BACKGROUND_COLOR = "#310161"
            SITE_FONT_COLOR = "white"
        elif IS_CANARY:
            SITE_BACKGROUND_COLOR = "#310161"
            SITE_FONT_COLOR = "white"
        else:
            SITE_BACKGROUND_COLOR = "#115852"
            SITE_FONT_COLOR = "white"

        random.shuffle(INSPIRATIONAL_MESSAGES)
        return render(
            request,
            "index.html",
            {
                "RELEASE_INFO": release_info,
                "DEPLOY_NOTES": f"API Version: {release_info.get('version')} |> Released by: {release_info.get('released_by')} On {release_info.get('release_date')}",
                "INSPIRATIONS": INSPIRATIONAL_MESSAGES,
                "SITE_TITLE": SITE_TITLE,
                "SITE_BACKGROUND_COLOR": SITE_BACKGROUND_COLOR,
                "SITE_FONT_COLOR": SITE_FONT_COLOR,
            },
        )

    def health_check(self, ctx: Context):
        return { "ok": True }, None


    def version(self, ctx: Context, args):
        return EnvConfig.release_info, None

    def create_carbon_equivalency(self, args) -> Tuple[dict, MassEnergizeAPIError]:
        carbon_data, err = self.store.create_carbon_equivalency(args)
        if err:
            return None, err
        return serialize(carbon_data), None

    def update_carbon_equivalency(self, args) -> Tuple[dict, MassEnergizeAPIError]:
        carbon_data, err = self.store.update_carbon_equivalency(args)
        if err:
            return None, err
        return serialize(carbon_data), None

    def get_carbon_equivalencies(self, args) -> Tuple[dict, MassEnergizeAPIError]:
        carbon_data, err = self.store.get_carbon_equivalencies(args)
        if err:
            return None, err
        if type(carbon_data) == QuerySet:
            return serialize_all(carbon_data), None
        else:
            return serialize(carbon_data), None

    def delete_carbon_equivalency(self, args) -> Tuple[dict, MassEnergizeAPIError]:
        carbon_data, err = self.store.delete_carbon_equivalency(args)
        if err:
            return None, err
        return serialize(carbon_data), None

    def authenticateFrontendInTestMode(self, args):
        passport_key = args.get("passport_key")
        if passport_key != TEST_PASSPORT_KEY:
            return None, CustomMassenergizeError("invalid_passport_key")
        user, err = self.store.authenticateFrontendInTestMode(args)
        if err:
            return None, CustomMassenergizeError(str(err))
        client = Client()
        return signinAs(client, user), None
    
    def load_menu_items(self,context, args):
        res, err = self.store.load_menu_items(context,args)
        if err:
            return None, err

        return res, None
    
    def create_menu(self, context, args):
        try:
            res, err = self.store.create_menu(context, args)
            
            if err:
                return None, err
            
            return serialize(res), None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def update_menu(self, context, args):
        try:
            res, err = self.store.update_menu(context, args)
            
            if err:
                return None, err
            
            return serialize(res), None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def delete_menu(self, context, args):
        try:
            res, err = self.store.delete_menu(context, args)
            
            if err:
                return None, err
            
            return res, None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def get_menu(self, context, args):
        try:
            res, err = self.store.get_menu(context, args)
            
            if err:
                return None, err
            
            return serialize(res), None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def reset_menu(self, context, args):
        try:
            res, err = self.store.reset_menu(context, args)
            
            if err:
                return None, err
            
            return serialize(res), None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def get_menus_for_admin(self, context, args):
        try:
            res, err = self.store.get_menus_for_admin(context, args)
            
            if err:
                return None, err
            
            return serialize_all(res), None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
    
    def get_internal_links(self, context, args):
        try:
            is_footer = args.get("is_footer", False)
            res, err = get_list_of_internal_links(is_footer)
            
            if err:
                return None, CustomMassenergizeError(str(err))
            
            return res, None
        
        except Exception as e:
            logging.error(f"GET_INTERNAL_LINKS_EXCEPTION_ERROR: {str(e)}")
            return None, CustomMassenergizeError(str(e))
    
    def list_all_languages(self, context, args) -> (dict, Exception):
        """
        Get all the languages
        """
        all_languages, err = self.store.list_all_languages(context, args)
        
        if err:
            return None, err
        
        return all_languages, None