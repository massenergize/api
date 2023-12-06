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

        self.add("/campaigns.technologies.add", self.add_campaign_technology)
        self.add("/campaigns.technologies.remove", self.remove_campaign_technology)

        self.add("/campaigns.technologies.testimonials.create", self.create_campaign_technology_testimonial)
        self.add("/campaigns.technologies.testimonials.update", self.update_campaign_technology_testimonial)
        self.add("/campaigns.technologies.testimonials.delete", self.delete_campaign_technology_testimonial)

        self.add("/campaigns.technologies.comments.create", self.create_campaign_technology_comment)
        self.add("/campaigns.technologies.comments.update", self.update_campaign_technology_comment)


        self.add("/campaigns.partners.add", self.add_campaign_partner)
        self.add("/campaigns.partners.remove", self.remove_campaign_partner)


        self.add("/campaigns.events.add", self.add_campaign_event)
        self.add("/campaigns.events.remove", self.remove_campaign_event)


        self.add("/campaigns.technologies.testimonials.list", self.list_campaign_technology_testimonials)
        self.add("/campaigns.technologies.comments.list", self.list_campaign_technology_comments)
        self.add("/campaigns.technologies.list", self.list_campaign_technologies)
        self.add("/campaigns.managers.list", self.list_campaign_managers)
        self.add("/campaigns.communities.list", self.list_campaign_communities)
        self.add("/campaigns.events.list", self.list_campaign_events)



        self.add("/campaigns.links.generate", self.generate_campaign_links)
        self.add("/campaigns.links.visits.count", self.campaign_link_visits_count)

        self.add("/campaigns.follow", self.add_campaign_follower)
        self.add("/campaigns.technology.like", self.add_campaign_technology_like)
        # self.add("/campaigns.technology.follow", self.add_campaign_technology_follower)
        self.add("/campaigns.technology.view", self.add_campaign_technology_view)
    

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

        self.validator.expect('campaign_account_id', str, is_required=False)
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

        self.validator.expect("community_id", str, is_required=False)
        self.validator.expect("action_ids", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.list_campaigns_for_admins(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def add_campaign_manager(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("user_ids", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_manager(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def remove_campaign_manager(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_manager_id", str, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.remove_campaign_manager(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)

    @admins_only
    def add_campaign_community(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("user_ids", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_community(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def remove_campaign_community(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_community_id", str, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.remove_campaign_community(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def add_campaign_technology(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("technology_id", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_technology(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def remove_campaign_technology(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_technology_id", str, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.remove_campaign_technology(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def create_campaign_technology_testimonial(self, request): 
        context: Context = request.context
        args: dict = context.args

        (self.validator
        .expect("campaign_technology_id", str, is_required=True)
        .expect("body", str, is_required=True)
        .expect("title", str, is_required=True)
        .expect("image", str, is_required=False)
        .expect("community_id", str, is_required=False)
        )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.create_campaign_technology_testimonial(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def update_campaign_technology_testimonial(self, request): 
        context: Context = request.context
        args: dict = context.args

        (self.validator
        .expect("id", str, is_required=True)
        .expect("body", str, is_required=False)
        .expect("title", str, is_required=False)
        .expect("image", str, is_required=False)
        .expect("community_id", str, is_required=False)
        .expect("is_approved", bool, is_required=False)
        .expect("is_published", bool, is_required=False)
        )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.update_campaign_technology_testimonial(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)

    def create_campaign_technology_comment(self, request): 
        context: Context = request.context
        args: dict = context.args

        (self.validator
        .expect("text", str, is_required=True)
        .expect("status", str, is_required=False)
        .expect("campaign_technology_id", str, is_required=False)
        )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.create_campaign_technology_comment(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def update_campaign_technology_comment(self, request): 
        context: Context = request.context
        args: dict = context.args

        (self.validator
        .expect("id", str, is_required=True)
        .expect("text", str, is_required=True)
        .expect("status", str, is_required=False)
        .expect("campaign_technology_id", str, is_required=False)
        )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.update_campaign_technology_comment(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def list_campaign_technology_testimonials(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_technology_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.list_campaign_technology_testimonials(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def list_campaign_technology_comments(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_technology_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.list_campaign_technology_comments(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def list_campaign_technologies(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.list_campaign_technologies(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def list_campaign_managers(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.list_campaign_managers(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def list_campaign_communities(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.list_campaign_communities(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def list_campaign_events(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.list_campaign_events(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def add_campaign_partner(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("partner_id", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_partner(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def remove_campaign_partner(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_partner_id", str, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.remove_campaign_partner(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def add_campaign_event(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("event_id", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_event(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    @admins_only
    def remove_campaign_event(self, request): 
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_event_id", str, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.remove_campaign_event(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def generate_campaign_links(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("campaign_id", str, is_required=True)
         .expect("url", str, is_required=True)
         .expect("utm_source", str, is_required=False)
          .expect("utm_medium", str, is_required=False)
          .expect("utm_campaign", str, is_required=False)
          .expect("utm_content", str, is_required=False)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.generate_campaign_links(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def campaign_link_visits_count(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("link_id", str, is_required=True)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.campaign_link_visits_count(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def add_campaign_follower(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("campaign_id", str, is_required=True)
         .expect("email", str, is_required=True)
         .expect("zipcode", str, is_required=True)
          .expect("community_id", int, is_required=False)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_follower(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    


    def add_campaign_technology_like(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("campaign_technology_id", str, is_required=True)
         .expect("user_id", int, is_required=False)
         .expect("zipcode", str, is_required=False)
         .expect("email", str, is_required=False)
          .expect("community_id", int, is_required=False)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_technology_like(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    

    def add_campaign_technology_view(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("campaign_technology_id", str, is_required=True)
         .expect("ip_address", str, is_required=False)
         .expect("user_agent", int, is_required=False)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_technology_view(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
    


    def delete_campaign_technology_testimonial(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.delete_campaign_technology_testimonial(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)
       
    

