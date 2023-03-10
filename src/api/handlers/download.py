from _main_.utils.route_handler import RouteHandler
from api.services.download import DownloadService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only

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
  

  @admins_only
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

    communities_data, err = self.service.metrics_download(context, args, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  @admins_only
  def send_cadmin_report(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    report, err = self.service.send_cadmin_report(context, community_id=community_id)
    print(report)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)

  @admins_only
  def send_sadmin_report(self, request):
    context: Context = request.context
    args: dict = context.args

    report, err = self.service.send_sadmin_report(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data={}, status=200)
