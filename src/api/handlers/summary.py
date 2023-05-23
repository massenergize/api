"""Handler file for all routes pertaining to summaries"""

from _main_.utils.route_handler import RouteHandler
from api.services.summary import SummaryService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only

class SummaryHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = SummaryService()
    self.registerRoutes()

  def registerRoutes(self):
    #admin routes
    self.add("/summary.next.steps.forAdmins", self.next_steps_for_admins)
    self.add("/summary.get.engagements", self.fetch_user_engagements_for_admins)
    self.add("/summary.listForCommunityAdmin", self.community_admin_summary)
    self.add("/summary.listForSuperAdmin", self.super_admin_summary)


  @admins_only 
  def fetch_user_engagements_for_admins(self, request): 
    context: Context = request.context
    args: dict = context.args
   
    self.validator.expect("is_community_admin", bool, is_required=False) # For manual testing 
    self.validator.expect("email", str, is_required=False) # For manual testing
     # from 15/05/2023: the variables above are no longer used for security reasons

    self.validator.expect("time_range", str, is_required=False) 
    self.validator.expect("start_time", str, is_required=False) 
    self.validator.expect("end_time", str, is_required=False) 
    self.validator.expect("communities", "str_list", is_required=False) 
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    content, err = self.service.fetch_user_engagements_for_admins(context, args)
    if err:
      return err
    return MassenergizeResponse(data=content)

  @admins_only  
  def next_steps_for_admins(self, request): 
    context: Context = request.context
    args: dict = context.args
    self.validator.expect("is_community_admin", bool, is_required=False) # For manual testing
    self.validator.expect("email", str, is_required=False) # For manual testing
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    content, err = self.service.next_steps_for_admins(context, args)
    if err:
      return err
    return MassenergizeResponse(data=content)
  @admins_only
  def community_admin_summary(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    summary, err = self.service.summary_for_community_admin(context, community_id)
    if err:
      return err
    return MassenergizeResponse(data=summary)

  @super_admins_only
  def super_admin_summary(self, request):
    context: Context = request.context
    args: dict = context.args
    summary, err = self.service.summary_for_super_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=summary)
