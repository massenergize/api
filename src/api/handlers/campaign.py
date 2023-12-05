from _main_.utils.context import Context
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only
from api.services.campaign import CampaignService


class CampaignHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = CampaignService()
        self.registerRoutes()

    def registerRoutes(self):
        self.add("/campaigns.info", self.info)
        self.add("/campaigns.create", self.create)
        self.add("/campaigns.list", self.list)
        self.add("/campaigns.update", self.update)
        self.add("/campaigns.delete", self.delete)

        self.add("/campaigns.managers.add", self.add_campaign_manager)
        self.add("/campaigns.managers.remove", self.remove_campaign_manager)

        self.add("/campaigns.communities.add", self.add_campaign_community)
        self.add("/campaigns.communities.remove", self.remove_campaign_community)

        # admin routes
        self.add("/campaigns.listForAdmin", self.list_campaigns_for_admins)

    def info(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        campaign_info, err = self.service.get_campaign_info(context, args)
        if err:
            return err
        return MassenergizeResponse(data=campaign_info)
    
    @admins_only
    def create(self, request): 
      context: Context = request.context
      args = context.get_request_body() 
      (self.validator
            .expect("title", str, is_required=True)
            .expect("start_date", str, is_required=False)
            .expect("logo", "str_list", is_required=False, options={"is_logo": True})
            .expect("description", str, is_required=True)
            .expect("campaign_account_id", str, is_required=True)
            .expect("is_global", bool, is_required=False)
            .expect("is_published", bool, is_required=False)
            .expect('is_approved', bool)
            .expect("is_template", bool, is_required=True)
            )

      args, err = self.validator.verify(args)
      if err:
        return err

      campaign_info, err = self.service.create_campaign(context, args)
      if err:
        return err
      return MassenergizeResponse(data=campaign_info)
    



    def list(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect('campaign_account_id', int, is_required=False)
        self.validator.expect('subdomain', str, is_required=False)

        args, err = self.validator.verify(args)
        if err:
            return err

        campaign_info, err = self.service.list_campaigns(context, args)

        if err:
            return err
        return MassenergizeResponse(data=campaign_info)


    @admins_only
    def update(self, request): 
        context: Context = request.context
        args = context.get_request_body() 
        (self.validator
        .expect("id", str, is_required=True)
        .expect("title", str, is_required=False,)
        .expect("start_date", str, is_required=False)
        .expect("logo", "str_list", is_required=False, options={"is_logo": True})
        .expect("end_date", str, is_required=False)
        .expect("is_global", bool, is_required=False)
        .expect("is_approved", bool, is_required=False)
        .expect("is_published", bool, is_required=False)
        .expect("description", str, is_required=False)
        .expect("is_template", bool, is_required=False)
        )


        args, err = self.validator.verify(args)
        if err:
            return err
        
        campaign_info, err = self.service.update_campaign(context, args)
        if err:
           return err      
        
        return MassenergizeResponse(data=campaign_info)
    

    @admins_only
    def delete(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
           return err   

        campaign_info, err = self.service.delete_campaign(context, args)
        if err:
            return err
        return MassenergizeResponse(data=campaign_info)
    

    @admins_only
    def list_campaigns_for_admins(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("community_id", int, is_required=False)
        self.validator.expect("action_ids", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        actions, err = self.service.list_campaigns_for_admins(context, args)
        if err:
          return err
        return MassenergizeResponse(data=actions)
    

    @admins_only
    def add_campaign_manager(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", int, is_required=False)
        self.validator.expect("user_ids", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        actions, err = self.service.add_campaign_manager(context, args)
        if err:
          return err
        return MassenergizeResponse(data=actions)
    

    @admins_only
    def remove_campaign_manager(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_manager_id", int, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        actions, err = self.service.remove_campaign_manager(context, args)
        if err:
          return err
        return MassenergizeResponse(data=actions)

    @admins_only
    def add_campaign_community(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", int, is_required=False)
        self.validator.expect("user_ids", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        actions, err = self.service.add_campaign_community(context, args)
        if err:
          return err
        return MassenergizeResponse(data=actions)
    

    @admins_only
    def remove_campaign_community(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_manager_id", int, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        actions, err = self.service.remove_campaign_community(context, args)
        if err:
          return err
        return MassenergizeResponse(data=actions)