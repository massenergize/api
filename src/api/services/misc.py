from django.test import Client
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
from database.models import Deployment
from _main_.settings import IS_PROD, IS_CANARY, BASE_DIR, TEST_PASSPORT_KEY
from _main_.utils.utils import load_json, load_text_contents
from django.db.models.query import QuerySet
from typing import Tuple

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

    def backfill(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        result, err = self.store.backfill(context, args)
        if err:
            return None, err
        return result, None
    def actions_report(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        result, err = self.store.actions_report(context, args)
        if err:
            return None, err
        return result, None

    def home(self, ctx: Context, request):
        deployments = Deployment.objects.all()[:3]
        build_info = load_json(BASE_DIR + "/_main_/config/build/deployConfig.json")
        deploy_notes = load_text_contents(
            BASE_DIR + "/_main_/config/build/deployNotes.txt"
        )

        deployment = Deployment.objects.filter(
            version=build_info.get("BUILD_VERSION", "")
        ).first()
        if deployment:
            if deployment.notes != deploy_notes:
                deployment.notes = deploy_notes
                deployment.save()
        else:
            deployment = Deployment.objects.create(
                version=build_info.get("BUILD_VERSION", ""), notes=deploy_notes
            )

        if IS_PROD:
            SITE_TITLE = "MassEnergize-API"
            SITE_BACKGROUND_COLOR = "#310161"
            SITE_FONT_COLOR = "white"
        elif IS_CANARY:
            SITE_TITLE = "CANARY: MassEnergize-API"
            SITE_BACKGROUND_COLOR = "#310161"
            SITE_FONT_COLOR = "white"
        else:
            SITE_TITLE = "DEV: MassEnergize-API"
            SITE_BACKGROUND_COLOR = "#0b5466"
            SITE_FONT_COLOR = "white"

        return render(
            request,
            "index.html",
            {
                "deployments": deployments,
                "BUILD_INFO": build_info,
                "DEPLOY_NOTES": deploy_notes,
                "SITE_TITLE": SITE_TITLE,
                "SITE_BACKGROUND_COLOR": SITE_BACKGROUND_COLOR,
                "SITE_FONT_COLOR": SITE_FONT_COLOR,
            },
        )

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
    
    
    # def load_essential_initial_site_data(self,context, args):
    #     res, err = self.store.load_essential_initial_site_data(context,args)
    #     if err:
    #         return None, err
    #
    #     return res, None
    
    def load_menu_items(self,context, args):
        res, err = self.store.load_menu_items(context,args)
        if err:
            return None, err
        
        return res, None
        
    
