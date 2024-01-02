from _main_.utils.context import Context
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only
from api.services.campaign_account import CampaignAccountService


class CampaignAccountHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = CampaignAccountService()
        self.registerRoutes()

    def registerRoutes(self):
        self.add("/campaigns.accounts.create", self.create_campaign_account)
        self.add("/campaigns.accounts.update", self.update_campaign_account)
        self.add("/campaigns.accounts.delete", self.delete_campaign_account)
        self.add("/campaigns.accounts.listForAdmin", self.list_campaign_accounts_for_admins)
        self.add("/campaigns.accounts.info", self.info)

        self.add("/campaigns.accounts.admin.add", self.add_admin)
        self.add("/campaigns.accounts.admin.remove", self.remove_admin)
        self.add("/campaigns.accounts.admin.update", self.update_admin)
    




    @admins_only
    def create_campaign_account(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("name", str, is_required=True)
         .expect("subdomain", str, is_required=True)
         .expect("community_id", str, is_required=True)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.create_campaign_account(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def update_campaign_account(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("id", str, is_required=True)
         .expect("name", str, is_required=False)
         .expect("subdomain", str, is_required=False)
         .expect("community", int, is_required=False)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.update_campaign_account(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def delete_campaign_account(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.delete_campaign_account(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def list_campaign_accounts_for_admins(self, request):
        context: Context = request.context
        args: dict = context.args

        res, err = self.service.list_campaign_accounts_for_admins(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def info(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        res, err = self.service.info(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def add_admin(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("campaign_account_id", str, is_required=True)
        self.validator.expect("user_id", int, is_required=True)
        self.validator.expect("role", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)

        res, err = self.service.add_admin(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def remove_admin(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("admin_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)

        res, err = self.service.remove_admin(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    
    @admins_only
    def update_admin(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("admin_id", str, is_required=True)
        self.validator.expect("role", bool, is_required=False)

        args, err = self.validator.verify(args, strict=True)

        res, err = self.service.update_admin(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)