from _main_.utils.route_handler import RouteHandler
from api.services.download import DownloadService
from _main_.utils.massenergize_response import MassenergizeResponse
from django.http import HttpResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
import csv

# see: https://docs.djangoproject.com/en/3.0/howto/outputting-csv/#streaming-csv-files

class DownloadHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = DownloadService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/downloads.users", self.users_download()) 
    self.add("/downloads.actions", self.actions_download())
    
  # TODO: a list of community ids instead? So super admins have the choice of doing some subset of communities?

  def users_download(self) -> function:
    def users_download_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop('community_id', None)
      users_download, err = self.service.users_download(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      response = HttpResponse(content_type="text/csv")
      response['Content-Disposition'] = 'attachment; filename="user-data.csv"'
      writer = csv.writer(response)
      for row in users_download:
        writer.write_row(row)
      return response
    return users_download_view

  def actions_download(self) -> function:
    def actions_download_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop('community_id', None)
      actions_download, err = self.service.actions_download(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      response = HttpResponse(content_type="text/csv")
      response['Content-Disposition'] = 'attachment; filename="user-data.csv"'
      writer = csv.writer(response)
      for row in actions_download:
        writer.write_row(row)
      return response
    return actions_download_view