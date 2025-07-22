from _main_.utils.route_handler import RouteHandler
from api.services.download import DownloadService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only

# see: https://docs.djangoproject.com/en/3.0/howto/outputting-csv

class DownloadHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = DownloadService()
    self.registerRoutes()


  def registerRoutes(self) -> None:
    self.add("/downloads.users", self.users_download) 
    self.add("/downloads.actions", self.actions_download)
    self.add("/downloads.communities", self.communities_download)
    self.add("/downloads.teams", self.teams_download)
    self.add("/downloads.metrics", self.metrics_download)
    self.add("/downloads.cadmin_report", self.send_cadmin_report)
    self.add("/downloads.sadmin_report", self.send_sadmin_report)
    self.add("/downloads.sample.user_report", self.send_sample_user_report)
    self.add("/downloads.action.users", self.action_users_download)
    self.add("/downloads.actions.users", self.actions_users_download)
    self.add("/downloads.pagemap", self.community_pagemap_download)
    self.add("/downloads.postmark.nudge_report", self.download_postmark_nudge_report)

  
    self.add("/downloads.campaigns.follows", self.campaign_follows_download)
    self.add("/downloads.campaigns.likes", self.campaign_likes_download)
    self.add("/downloads.campaigns.link_performance", self.campaign_link_performance_download)
    self.add("/downloads.campaigns.performance", self.campaign_performance_download)
    self.add("/downloads.campaigns.technology.performance", self.campaign_tech_performance_download)
    self.add("/downloads.campaigns.views.performance", self.campaign_views_performance_download)
    self.add("/downloads.campaigns.interaction.performance", self.campaign_interaction_performance_download)

    self.add("/export.actions", self.export_actions)
    self.add("/export.events", self.export_events)
    self.add("/export.testimonials", self.export_testimonials)
    self.add("/export.cc.actions", self.export_cc_actions)
    self.add("/export.vendors", self.export_vendors)
    


  @admins_only
  def users_download(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    team_id = args.pop('team_id', None)

    users_data, err = self.service.users_download(context, community_id=community_id, team_id=team_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)


  @admins_only
  def actions_download(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    actions_data, err = self.service.actions_download(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
  

  @super_admins_only
  def communities_download(self, request):
    context: Context = request.context
    #args: dict = context.args
    communities_data, err = self.service.communities_download(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)


  @admins_only
  def teams_download(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    teams_data, err = self.service.teams_download(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
  
  @admins_only
  def metrics_download(self, request):
    context: Context = request.context
    args: dict = context.args

    community_id = args.pop('community_id', None)
    audience = args.pop('audience', None)
    report_community_ids = args.pop('community_ids', None)

    communities_data, err = self.service.metrics_download(context, args, community_id, audience, report_community_ids)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  @admins_only
  def send_cadmin_report(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    report, err = self.service.send_cadmin_report(context, community_id=community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  def send_sample_user_report(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    report, err = self.service.send_sample_user_report(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  @super_admins_only
  def send_sadmin_report(self, request):
    context: Context = request.context
    args: dict = context.args

    report, err = self.service.send_sadmin_report(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  @admins_only
  def action_users_download(self, request):
    context: Context = request.context
    args: dict = context.args
    action_id = args.pop('action_id', None)
    _, err = self.service.action_users_download(context, action_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  @admins_only
  def actions_users_download(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    _, err = self.service.actions_users_download(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  @admins_only
  def policy_download(self, request):
    context: Context = request.context
    args: dict = context.args
    report, err = self.service.policy_download(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  #@admins_only
  def community_pagemap_download(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    
    report, err = self.service.community_pagemap_download(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
  

  @admins_only
  def campaign_follows_download(self, request):
    context: Context = request.context
    args: dict = context.args
    campaign_id = args.pop('campaign_id', None)
    report, err = self.service.campaign_follows_download(context, campaign_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=report, status=200)
  

  @admins_only
  def campaign_likes_download(self, request):
    context: Context = request.context
    args: dict = context.args
    campaign_id = args.pop('campaign_id', None)
    report, err = self.service.campaign_likes_download(context, campaign_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=report, status=200)
  

  @admins_only
  def campaign_link_performance_download(self, request):
    context: Context = request.context
    args: dict = context.args
    campaign_id = args.pop('campaign_id', None)
    report, err = self.service.campaign_link_performance_download(context, campaign_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=report, status=200)
  

  @admins_only
  def campaign_performance_download(self, request):
    context: Context = request.context
    args: dict = context.args
    campaign_id = args.pop('campaign_id', None)
    report, err = self.service.campaign_performance_download(context, campaign_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=report, status=200)
  

  @admins_only
  def campaign_tech_performance_download(self, request):
    context: Context = request.context
    args: dict = context.args
    campaign_id = args.pop('campaign_id', None)
    report, err = self.service.campaign_tech_performance_download(context, campaign_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=report, status=200)
  

  @admins_only
  def campaign_views_performance_download(self, request):
    context: Context = request.context
    args: dict = context.args
    campaign_id = args.pop('campaign_id', None)
    report, err = self.service.campaign_views_performance_download(context, campaign_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=report, status=200)
  

  @admins_only
  def campaign_interaction_performance_download(self, request):
    context: Context = request.context
    args: dict = context.args
    campaign_id = args.pop('campaign_id', None)
    report, err = self.service.campaign_interaction_performance_download(context, campaign_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=report, status=200)
  
  
  
  @admins_only
  def download_postmark_nudge_report(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    period = args.get("period")
    report, err = self.service.download_postmark_nudge_report(context, community_id=community_id, period=period)
    
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
  

  # @admins_only
  def export_actions(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    email = args.pop('email', None)

    report, err = self.service.export_actions(context, community_id=community_id, email=email)
    
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
  
  # @admins_only
  def export_events(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    email = args.pop('email', None)

    report, err = self.service.export_events(context, community_id=community_id, email=email)
    
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
  
  # @admins_only
  def export_testimonials(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    email = args.pop('email', None)
    report, err = self.service.export_testimonials(context, community_id=community_id, email=email)
    
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
  

  @admins_only
  def export_cc_actions(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    email = args.get('email', None)

    report, err = self.service.export_cc_actions(context, community_id=community_id, email=email)
    
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
  

  @admins_only
  def export_vendors(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    email = args.get('email', None)

    report, err = self.service.export_vendors(context, community_id=community_id, email=email)
    
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)