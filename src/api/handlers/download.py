from _main_.utils.route_handler import RouteHandler
from api.services.download import DownloadService
from _main_.utils.massenergize_response import MassenergizeResponse
from django.http import HttpResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required
import csv

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


  def _get_csv_response(self, data, download_type, community_name=None):
    response = HttpResponse(content_type="text/csv")
    if not community_name:
      filename = "all-%s-data.csv" % download_type
    else:
      filename = "%s-%s-data.csv" % (community_name, download_type)
    response['Access-Control-Expose-Headers'] = 'Content-Disposition'
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    writer = csv.writer(response)
    for row in data:
      writer.writerow(row)
    return response


  @admins_only
  def users_download(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    team_id = args.pop('team_id', None)

    (users_data, community_name), err = self.service.users_download(context, community_id=community_id, team_id=team_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return self._get_csv_response(data=users_data, download_type='users', community_name=community_name)


  @admins_only
  def actions_download(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    (actions_data, community_name), err = self.service.actions_download(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return self._get_csv_response(data=actions_data, download_type='actions', community_name=community_name)


  @admins_only
  def communities_download(self, request):
    context: Context = request.context
    #args: dict = context.args
    (communities_data, dummy), err = self.service.communities_download(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return self._get_csv_response(data=communities_data, download_type='communities')


  @admins_only
  def teams_download(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    (teams_data, community_name), err = self.service.teams_download(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return self._get_csv_response(data=teams_data, download_type='teams', community_name=community_name)
