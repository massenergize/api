from _main_.utils.route_handler import RouteHandler
from api.services.download import DownloadService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator


class DownloadHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = DownloadService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/downloads.users", self.users_download()) 
    self.add("/downloads.actions", self.actions_download())
    
  # TODO: implement handlers