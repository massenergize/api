"""Handler file for all routes pertaining to goals"""
import os

from _main_.utils.route_handler import RouteHandler
from api.services.misc import MiscellaneousService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only, x_frame_options_exempt
from database.utils.settings.admin_settings import AdminPortalSettings
from database.utils.settings.user_settings import UserPortalSettings
from django.http import JsonResponse
from django.shortcuts import render



class MiscellaneousHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = MiscellaneousService()
        self.registerRoutes()

    def registerRoutes(self) -> None:
        self.add("/menus.remake", self.remake_navigation_menu)
        self.add("/menus.list", self.navigation_menu_list)
        self.add("/user.portal.menu.list", self.load_menu_items)
        self.add("/data.backfill", self.backfill)
        self.add("/data.carbonEquivalency.create", self.create_carbon_equivalency)
        self.add("/data.carbonEquivalency.update", self.update_carbon_equivalency)
        self.add("/data.carbonEquivalency.get", self.get_carbon_equivalencies)
        self.add("/data.carbonEquivalency.info", self.get_carbon_equivalencies)
        self.add("/data.carbonEquivalency.delete", self.delete_carbon_equivalency)
        self.add("/home", self.home)
        self.add("/health_check", self.health_check)
        self.add("/version", self.version)
        self.add("/auth.login.testmode", self.authenticateFrontendInTestMode)
        self.add("", self.home)
        # settings should be called preferences
        self.add("/preferences.list", self.fetch_available_preferences)
        self.add("/settings.list", self.fetch_available_preferences)
        self.add("/what.happened", self.fetch_footages)
        self.add("/actions.report", self.actions_report)
        self.add("/rewiring_america", self.get_rewiring_america_data)
        
        self.add("/menus.create", self.create_menu)
        self.add("/menus.update", self.update_menu)
        self.add("/menus.delete", self.delete_menu)
        self.add("/menus.get", self.get_menu)
        self.add("/menus.reset", self.reset_menu)
        self.add("/menus.listForAdmins", self.get_menus_for_admin)
        self.add("/links.internal.get", self.get_internal_links)
        
        self.add("/translations.languages.list", self.list_all_languages)


    @admins_only
    def fetch_footages(self, request):
        context: Context = request.context
        footages, error = self.service.fetch_footages(context,context.args)
        if error:
            return MassenergizeResponse(error=error)
        return MassenergizeResponse(data=footages)

    def fetch_available_preferences(self, request):
        context: Context = request.context
        args:dict = context.args
        if context.user_is_admin():
            return MassenergizeResponse(data=UserPortalSettings.Preferences if args.get("subdomain") else AdminPortalSettings.Preferences)
        return MassenergizeResponse(data=UserPortalSettings.Preferences)

    def remake_navigation_menu(self, request):
        data, err = self.service.remake_navigation_menu()
        if err:
            return MassenergizeResponse(error=err)
        return MassenergizeResponse(data=data)

    def navigation_menu_list(self, request):
        context: Context = request.context
        args: dict = context.args
        goal_info, err = self.service.navigation_menu_list(context, args)
        if err:
            return err
        return MassenergizeResponse(data=goal_info)

    def backfill(self, request):
        context: Context = request.context
        args: dict = context.args
        goal_info, err = self.service.backfill(context, args)
        if err:
            return err
        return MassenergizeResponse(data=goal_info)

    def actions_report(self, request):
        context: Context = request.context
        args: dict = context.args
        print("Got here")
        goal_info, err = self.service.actions_report(context, args)
        if err:
            return err
        return MassenergizeResponse(data=goal_info)

    @super_admins_only
    def create_carbon_equivalency(self, request):
        context: Context = request.context
        args: dict = context.args

        carbon_info, err = self.service.create_carbon_equivalency(args)

        if err:
            return err
        return MassenergizeResponse(data=carbon_info)

    @super_admins_only
    def update_carbon_equivalency(self, request):
        context: Context = request.context
        args: dict = context.args

        # if id passed, return just one, otherwise all
        self.validator.expect("id", int, is_required=True)
        self.validator.rename("carbon_equivalency_id", "id")
        args, err = self.validator.verify(args)

        carbon_info, err = self.service.update_carbon_equivalency(args)

        if err:
            return err
        return MassenergizeResponse(data=carbon_info)
    
    def get_carbon_equivalencies(self, request):
        context: Context = request.context
        args: dict = context.args

        # if id passed, return just one, otherwise all
        self.validator.expect("id", int)
        self.validator.rename("carbon_equivalency_id", "id")
        args, err = self.validator.verify(args)

        carbon_info, err = self.service.get_carbon_equivalencies(args)

        if err:
            return err
        return MassenergizeResponse(data=carbon_info)
    @super_admins_only
    def delete_carbon_equivalency(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", int, is_required=True)
        self.validator.rename("carbon_equivalency_id", "id")
        args, err = self.validator.verify(args)

        carbon_info, err = self.service.delete_carbon_equivalency(args)

        if err:
            return err
        return MassenergizeResponse(data=carbon_info)

    def home(self, request):
        context: Context = request.context
        return self.service.home(context, request)

    def health_check(self, request):
        context: Context = request.context
        data, err = self.service.health_check(context)
        if err:
            return MassenergizeResponse(data=data, error=err)
        return JsonResponse(data=data, safe=False)

    def version(self, request):
        context: Context = request.context
        data, err = self.service.version(context, request)
        if err:
            return MassenergizeResponse(data=data, error=err)
        return JsonResponse(data=data, safe=False)


    def authenticateFrontendInTestMode(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("passport_key", str, is_required=True)
        self.validator.expect("email", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
            return err

        token, error = self.service.authenticateFrontendInTestMode(args)
        if error:
            return MassenergizeResponse(error=str(error), status=error.status)

        response = MassenergizeResponse(data=token)
        response.set_cookie(
            "token", value=token, max_age=24 * 60 * 60, samesite="Strict"
        )
        return response
    
    def load_menu_items(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("community_id", is_required=False)
        self.validator.expect("subdomain", is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return MassenergizeResponse(error=err)
        
        data, err = self.service.load_menu_items(context, args)
        if err:
            return err
        return MassenergizeResponse(data=data)
    
    
    @admins_only
    def create_menu(self, request):
        try:
            context: Context = request.context
            args: dict = context.args
            
            self.validator.expect("community_id", int, is_required=False)
            self.validator.expect("subdomain", str, is_required=False)
            
            args, err = self.validator.verify(args, strict=True)
            if err:
                return err

            menu, err = self.service.create_menu(context, args)
            
            if err:
                return err
            
            return MassenergizeResponse(data=menu)
        
        except Exception as e:
            return MassenergizeResponse(error=str(e))
        
    @admins_only
    def update_menu(self, request):
        try:
            context: Context = request.context
            args: dict = context.args
            
            self.validator.expect("id", int, is_required=True)
            self.validator.expect("content", dict, is_required=False)
            self.validator.expect("name", str, is_required=False)
            self.validator.expect("is_published", bool, is_required=False)
            self.validator.expect("community_logo_link", str, is_required=False)
            self.validator.expect("footer_content", dict, is_required=False)
            self.validator.expect("contact_info", dict, is_required=False)
            self.validator.expect("community_logo_id", int, is_required=False)
            
            args, err = self.validator.verify(args, strict=True)
            
            if err:
                return err

            menu, err = self.service.update_menu(context, args)
            
            if err:
                return err
            
            return MassenergizeResponse(data=menu)
        
        except Exception as e:
            return MassenergizeResponse(error=str(e))
        
    @admins_only
    def delete_menu(self, request):
        try:
            context: Context = request.context
            args: dict = context.args
            
            self.validator.expect("id", int, is_required=True)
            
            args, err = self.validator.verify(args, strict=True)
            if err:
                return err
            
            menu, err = self.service.delete_menu(context, args)
            
            if err:
                return err
            
            return MassenergizeResponse(data=menu)
        
        except Exception as e:
            return MassenergizeResponse(error=str(e))
        
    @admins_only
    def get_menu(self, request):
        try:
            context: Context = request.context
            args: dict = context.args
            
            self.validator.expect("id", int, is_required=True)
            
            args, err = self.validator.verify(args, strict=True)
            if err:
                return err
            
            menu, err = self.service.get_menu(context, args)
            
            if err:
                return err
            
            return MassenergizeResponse(data=menu)
        
        except Exception as e:
            return MassenergizeResponse(error=str(e))
        
        
    @admins_only
    def reset_menu(self, request):
        try:
            context: Context = request.context
            args: dict = context.args
            
            self.validator.expect("id", int, is_required=True)
            
            args, err = self.validator.verify(args, strict=True)
            if err:
                return err
            
            menu, err = self.service.reset_menu(context, args)
            
            if err:
                return err
            
            return MassenergizeResponse(data=menu)
        
        except Exception as e:
            return MassenergizeResponse(error=str(e))
    
    @admins_only
    def get_menus_for_admin(self, request):
        try:
            context: Context = request.context
            args: dict = context.args
            
            self.validator.expect("community_id", int, is_required=False)
            self.validator.expect("subdomain", str, is_required=False)
            
            args, err = self.validator.verify(args, strict=True)
            if err:
                return err
                
            data, err = self.service.get_menus_for_admin(context, args)
            if err:
                return err
            return MassenergizeResponse(data=data)
        
        except Exception as e:
            return MassenergizeResponse(error=str(e))
    
    def get_internal_links(self, request):
        try:
            context: Context = request.context
            args: dict = context.args
            
            self.validator.expect("is_footer", bool, is_required=False)
            
            args, err = self.validator.verify(args, strict=True)
            if err:
                return err
            
            data, err = self.service.get_internal_links(context, args)
            if err:
                return err
            return MassenergizeResponse(data=data)
        
        except Exception as e:
            return MassenergizeResponse(error=str(e))
    
    @x_frame_options_exempt
    def get_rewiring_america_data(self, request):
        args = {"rewiring_america": os.environ.get('REWIRING_AMERICA_API_KEY') }
        return render(request, "rewiring_america.html", args)
    
    @admins_only
    def list_all_languages(self, request):
        context: Context = request.context
        args: dict = context.args
        
        args, err = self.validator.verify(args)
        
        if err:
            return err
        
        all_languages, err = self.service.list_all_languages(context, args)
        if err:
            return err
        return MassenergizeResponse(data=all_languages)
        
