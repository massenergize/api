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
        self.add("/campaigns.infoForUser", self.get_campaign_info_for_user)
        self.add("/campaigns.create", self.create) #Not used at the moment

        self.add("/campaigns.createFromTemplate", self.create_campaign_from_template)

        self.add("/campaigns.list", self.list)
        self.add("/campaigns.update", self.update)
        self.add("/campaigns.delete", self.delete)

        self.add("/campaigns.config.create", self.create_campaign_config) # Not used at the moment
        self.add("/campaigns.config.update", self.update_campaign_config) # Not used at the moment
        self.add("/campaigns.config.info", self.get_campaign_config) # Not used at the moment

        self.add("/campaigns.navigation.create", self.create_campaign_navigation) # Not used at the moment
        self.add("/campaigns.stats.get", self.get_campaign_analytics)

        self.add("/campaigns.managers.add", self.add_campaign_manager)
        self.add("/campaigns.managers.remove", self.remove_campaign_manager)
        self.add("/campaigns.managers.update", self.update_campaign_manager)
        self.add("/campaigns.managers.updateKeyContact", self.update_campaign_key_contact)

        self.add("/campaigns.communities.add", self.add_campaign_community)
        self.add("/campaigns.communities.remove", self.remove_campaign_community)
        self.add("/campaigns.communities.update", self.update_campaign_community)

        self.add("/campaigns.technologies.add", self.add_campaign_technology)
        self.add("/campaigns.technologies.create", self.create_campaign_technology)
        self.add("/campaigns.technologies.remove", self.remove_campaign_technology)
        self.add("/campaigns.technologies.update", self.update_campaign_technology)
        self.add("/campaigns.technologies.info", self.get_campaign_technology_info)

        self.add("/campaigns.technologies.testimonials.create", self.create_campaign_technology_testimonial)
        self.add("/campaigns.technologies.testimonials.add", self.add_campaign_technology_testimonial)
        self.add("/campaigns.technologies.testimonials.update", self.update_campaign_technology_testimonial)
        self.add("/campaigns.technologies.testimonials.delete", self.delete_campaign_technology_testimonial)
        self.add("/campaigns.technologies.testimonials.info", self.get_campaign_technology_testimonial)

        self.add("/campaigns.technologies.comments.create", self.create_campaign_technology_comment)
        self.add("/campaigns.technologies.comments.update", self.update_campaign_technology_comment)
        self.add("/campaigns.technologies.comments.delete", self.delete_campaign_technology_comment)


        self.add("/campaigns.partners.add", self.add_campaign_partner) # Not used at the moment
        self.add("/campaigns.partners.remove", self.remove_campaign_partner) # Not used at the moment


        self.add("/campaigns.technology.events.add", self.add_campaign_technology_event)
        self.add("/campaigns.technology.events.remove", self.remove_campaign_technology_event)
        self.add("/campaigns.technology.events.list", self.list_campaign_technology_event) # Not used at the moment


        self.add("/campaigns.testimonials.list", self.list_campaign_technology_testimonials)
        self.add("/campaigns.comments.list", self.list_campaign_technology_comments)
        self.add("/campaigns.technologies.list", self.list_campaign_technologies) # Not used at the moment
        self.add("/campaigns.managers.list", self.list_campaign_managers)
        self.add("/campaigns.communities.list", self.list_campaign_communities)

        self.add("/campaigns.links.generate", self.generate_campaign_links)
        self.add("/campaigns.links.visits.count", self.campaign_link_visits_count) # Not used at the moment

        self.add("/campaigns.follow", self.add_campaign_follower)
        self.add("/campaigns.technology.follow", self.add_campaign_technology_follower)
        self.add("/campaigns.technology.like", self.add_campaign_technology_like)
        self.add("/campaigns.like", self.add_campaign_like)

        self.add("/campaigns.technology.view", self.add_campaign_technology_view)
        self.add("/campaigns.view", self.add_campaign_view)

        # admin routes
        self.add("/campaigns.listForAdmin", self.list_campaigns_for_admins)
        self.add("/campaigns.ownership.transfer", self.transfer_ownership)

        self.add("/campaigns.activities.track", self.track_activity)


        # for ease
        self.add("/campaigns.communities.events.list", self.list_campaign_communities_events)
        self.add("/campaigns.communities.testimonials.list", self.list_campaign_communities_testimonials)
        self.add("/campaigns.communities.vendors.list", self.list_campaign_communities_vendors)
        self.add("/call.to.action.delete", self.delete_call_to_action)
        
        self.add("/campaigns.media.add", self.add_campaign_media)
        self.add("/campaigns.media.delete", self.delete_campaign_media)
        self.add("/campaigns.media.update", self.update_campaign_media)


    @admins_only
    def info(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True).expect("email", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        campaign_info, err = self.service.get_campaign_info(context, args)
        if err:
            return err

        return MassenergizeResponse(data=campaign_info)



    def get_campaign_info_for_user(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=False).expect("email", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        campaign_info, err = self.service.get_campaign_info_for_user(context, args)
        if err:
            return err

        return MassenergizeResponse(data=campaign_info)

    @admins_only
    def create(self, request):
      context: Context = request.context
      args = context.get_request_body()
      (self.validator
            .expect("title", str, is_required=True)
            .expect("tagline", str, is_required=False)
            .expect("start_date", str, is_required=False)
            .expect("primary_logo", "file", is_required=False, options={"is_logo": True})
            .expect("secondary_logo", "file", is_required=False, options={"is_logo": True})
            .expect("campaign_image", "file", is_required=False, options={"is_logo": True})
            .expect("key_contact_image", "file", is_required=False, options={"is_logo": True})
            .expect("description", str, is_required=True)
            .expect("campaign_account_id", str, is_required=True)
            .expect("is_global", bool, is_required=False)
            .expect("is_published", bool, is_required=False)
            .expect('is_approved', bool)
            .expect("is_template", bool, is_required=True)
      )

      args, err = self.validator.verify(args, strict=True)
      if err:
        return err

      campaign_info, err = self.service.create_campaign(context, args)
      if err:
        return err
      return MassenergizeResponse(data=campaign_info)


    @admins_only
    def create_campaign_from_template(self, request):
       context: Context = request.context
       args = context.args

      #  self.validator.expect("template_id", str, is_required=False)
       self.validator.expect("campaign_account_id", str, is_required=True)
       self.validator.expect("title", str, is_required=True)
       self.validator.expect("community_ids", "str_list", is_required=True)
       self.validator.expect("template_key", str, is_required=False)

       args, err = self.validator.verify(args)
       if err:
          return err

       campaign_info, err = self.service.create_campaign_from_template(context, args)
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
        .expect("tagline", str, is_required=False,)
        .expect("start_date", str, is_required=False)
        .expect("primary_logo", "file", is_required=False, options={"is_logo": True})
        .expect("secondary_logo", "file", is_required=False, options={"is_logo": True})
        .expect("campaign_image", "file", is_required=False, options={"is_logo": True})
        .expect("end_date", str, is_required=False)
        .expect("is_global", bool, is_required=False)
        .expect("is_approved", bool, is_required=False)
        .expect("is_published", bool, is_required=False)
        .expect("description", str, is_required=False)
        .expect("is_template", bool, is_required=False)
        .expect("communities_section", dict, is_required=False)
        .expect("technologies_section", dict, is_required=False)
        .expect("newsletter_section", dict, is_required=False)
        .expect("coaches_section", dict, is_required=False)
        .expect("about_us_title", str, is_required=False)
         .expect("template_key", str, is_required=False)
        .expect("banner", "file", is_required=False)
        .expect("goal_section", dict, is_required=False)
        .expect("callout_section", dict, is_required=False)
        .expect("contact_section", dict, is_required=False)
         .expect("call_to_action", dict, is_required=False)
         .expect("banner_section", dict, is_required=False)
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

        res, err = self.service.list_campaigns_for_admins(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
    def add_campaign_manager(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("email", str, is_required=False)
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
    def update_campaign_manager(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_manager_id", str, is_required=True)
        self.validator.expect("is_key_contact", bool, is_required=False)
        self.validator.expect("contact", str, is_required=False)
        self.validator.expect("role", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err
        res, err = self.service.update_campaign_manager(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)



    @admins_only
    def add_campaign_community(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("community_ids", "str_list", is_required=False)
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

        self.validator.expect("id", str, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.remove_campaign_community(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
    def update_campaign_community(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_community_id", str, is_required=True)
        self.validator.expect("help_link", str, is_required=False)
        self.validator.expect("alias", str, is_required=False)
        self.validator.expect("extra_links", dict, is_required=False)

        args, err = self.validator.verify(args)
        if err:
          return err
        res, err = self.service.update_campaign_community(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
    def add_campaign_technology(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("technology_ids", "str_list", is_required=True)
        # self.validator.expect("overview_title", str, is_required=False)
        # self.validator.expect("actions_section", str, is_required=False)
        # self.validator.expect("coaches_section", str, is_required=False)
        # self.validator.expect("deal_section", str, is_required=False)
        # self.validator.expect("vendors_section", str, is_required=False)
        # self.validator.expect("more_info_section", str, is_required=False)
        # self.validator.expect("deal_section_image", "file", is_required=False)

        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_technology(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
    def update_campaign_technology(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("technology_id", str, is_required=False)
        # self.validator.expect("overview_title", str, is_required=False)
        # self.validator.expect("actions_section", str, is_required=False)
        # self.validator.expect("coaches_section", str, is_required=False)
        # self.validator.expect("deal_section", str, is_required=False)
        # self.validator.expect("vendors_section", str, is_required=False)
        # self.validator.expect("more_info_section", str, is_required=False)
        # self.validator.expect("deal_section_image", "file", is_required=False)

        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.update_campaign_technology(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
    def remove_campaign_technology(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=False)
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
        .expect("image", "file", is_required=False)
        .expect("community_id", str, is_required=False)
        .expect("user_id", str, is_required=False)
        .expect("name", str, is_required=False)
        .expect("email", str, is_required=False)
        .expect("is_published", bool, is_required=False)
        )
        args, err = self.validator.verify(args, strict=True)
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
        # .expect("image", "file", is_required=False)
        .expect("community_id", str, is_required=False)
        .expect("is_approved", bool, is_required=False)
        .expect("is_published", bool, is_required=False)
         .expect("is_featured", bool, is_required=False)
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
        .expect("community_id", int, is_required=False)
        .expect("campaign_technology_id", str, is_required=False)
        .expect("user_id", str, is_required=False)
        .expect("is_from_admin_site", bool, is_required=False)
        )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.create_campaign_technology_comment(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)

    @admins_only
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
        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.list_campaign_technology_testimonials(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def list_campaign_technology_comments(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args, strict=True)
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

    @admins_only
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

    @admins_only
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


    def list_campaign_technology_event(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_technology_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.list_campaign_technology_event(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
    def add_campaign_partner(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=False)
        self.validator.expect("partner_ids", "str_list", is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_partners(context, args)
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

        res, err = self.service.remove_campaign_partners(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
    def add_campaign_technology_event(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_technology_id", str, is_required=False)
        self.validator.expect("event_ids", list, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_technology_event(context, args)
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
         .expect("email", str, is_required=True)
         .expect("zipcode", str, is_required=False)
          .expect("community_id", int, is_required=False)
          .expect("campaign_id", str, is_required=False)
          .expect("is_other", bool, is_required=False)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_follower(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def add_campaign_technology_follower(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("campaign_technology_id", str, is_required=True)
         .expect("email", str, is_required=True)
          .expect("community_id", int, is_required=False)
          .expect("campaign_id", str, is_required=False)
          .expect("is_other", bool, is_required=False)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_technology_follower(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)



    def add_campaign_technology_like(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("campaign_technology_id", str, is_required=True))
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
         .expect("url", str, is_required=True)
          .expect("email", str, is_required=False)
          )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_technology_view(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
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


    @admins_only
    def get_campaign_analytics(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.get_campaign_analytics(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def add_campaign_like(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.add_campaign_like(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)

    @admins_only
    def transfer_ownership(self, request):
        context: Context = request.context
        args: dict = context.args

        (self.validator
         .expect("campaign_id", str, is_required=True)
         .expect("user_id", int, is_required=True)
         )
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.transfer_ownership(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def get_campaign_technology_info(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_technology_id", str, is_required=True)
        self.validator.expect("email", str, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.get_campaign_technology_info(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def get_campaign_config(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.get_campaign_config(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def create_campaign_config(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        self.validator.expect("advert", str, is_required=False)
        self.validator.expect("theme", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.create_campaign_config(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def update_campaign_config(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("advert", str, is_required=False)
        self.validator.expect("theme", str, is_required=False)
        args, err = self.validator.verify(args)
        if err:
          return err

        res, err = self.service.update_campaign_config(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def get_campaign_technology_testimonial(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.get_campaign_technology_testimonial(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)



    def create_campaign_navigation(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.create_campaign_navigation(context, args)
        if err:
          return err

        return MassenergizeResponse(data=res)



    def track_activity(self, request):
      context: Context = request.context
      args: dict = context.args

      self.validator.expect("campaign_id", str, is_required=True)
      self.validator.expect("source", str, is_required=True)
      self.validator.expect("target", str, is_required=False)
      self.validator.expect("email", str, is_required=True)
      self.validator.expect("button_type", str, is_required=False)

      args, err = self.validator.verify(args, strict=True)
      if err:
        return err

      res, err = self.service.track_activity(context, args)
      if err:
        return err

      return MassenergizeResponse(data=res)



    def add_campaign_view(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        self.validator.expect("url", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.add_campaign_view(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    def delete_campaign_technology_comment(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", str, is_required=True)
        self.validator.expect("user_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.delete_campaign_technology_comment(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)


    @admins_only
    def create_campaign_technology(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)
        self.validator.expect("name", str, is_required=True)
        self.validator.expect("description", str, is_required=True)
        self.validator.expect("image", "file", is_required=False)
        self.validator.expect("summary", str, is_required=False)
        self.validator.expect("campaign_account_id", str, is_required=True)
        self.validator.expect("help_link", str, is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.create_campaign_technology(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)



    @admins_only
    def list_campaign_communities_events(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.list_campaign_communities_events(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)

    @admins_only
    def list_campaign_communities_testimonials(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.list_campaign_communities_testimonials(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)

    @admins_only
    def list_campaign_communities_vendors(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("campaign_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.list_campaign_communities_vendors(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)

    @admins_only
    def add_campaign_technology_testimonial(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("technology_id", str, is_required=True)
        self.validator.expect("campaign_id", str, is_required=True)
        self.validator.expect("testimonial_ids", list, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
          return err

        res, err = self.service.add_campaign_technology_testimonial(context, args)
        if err:
          return err
        return MassenergizeResponse(data=res)

    @admins_only
    def remove_campaign_technology_event(self, request):
      context: Context = request.context
      args: dict = context.args

      self.validator.expect("id", str, is_required=True)

      args, err = self.validator.verify(args, strict=True)
      if err:
        return err

      res, err = self.service.remove_campaign_technology_event(context, args)
      if err:
        return err
      return MassenergizeResponse(data=res)

    @admins_only
    def update_campaign_key_contact(self, request):
      context: Context = request.context
      args: dict = context.args

      self.validator.expect("campaign_id", str, is_required=True)
      self.validator.expect("manager_id", str, is_required=True)

      args, err = self.validator.verify(args, strict=True)
      if err:
        return err

      res, err = self.service.update_campaign_key_contact(context, args)
      if err:
        return err
      return MassenergizeResponse(data=res)


    @admins_only
    def delete_call_to_action(self, request):
      context: Context = request.context
      args: dict = context.args

      print(args)

      self.validator.expect("id", str, is_required=True)

      args, err = self.validator.verify(args, strict=True)
      if err:
        return err

      res, err = self.service.delete_call_to_action(context, args)
      if err:
        return err
      return MassenergizeResponse(data=res)
    
    
    @admins_only
    def add_campaign_media(self, request):
      context: Context = request.context
      args: dict = context.args

      self.validator.expect("campaign_id", str, is_required=True)
      self.validator.expect("media", "file", is_required=True)
      self.validator.expect("order", int, is_required=True)

      args, err = self.validator.verify(args, strict=True)
      if err:
        return err

      res, err = self.service.add_campaign_media(context, args)
      if err:
        return err
      return MassenergizeResponse(data=res)
    
    
    @admins_only
    def delete_campaign_media(self, request):
      context: Context = request.context
      args: dict = context.args

      self.validator.expect("id", str, is_required=True)

      args, err = self.validator.verify(args, strict=True)
      if err:
        return err

      res, err = self.service.delete_campaign_media(context, args)
      if err:
        return err
      return MassenergizeResponse(data=res)
    
    
    @admins_only
    def update_campaign_media(self, request):
      context: Context = request.context
      args: dict = context.args

      self.validator.expect("id", str, is_required=True)
      self.validator.expect("order", int, is_required=False)
      self.validator.expect("media", "file", is_required=False)

      args, err = self.validator.verify(args, strict=True)
      if err:
        return err

      res, err = self.service.update_campaign_media(context, args)
      if err:
        return err
      return MassenergizeResponse(data=res)







