"""Handler file for all routes pertaining to goals"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.misc import MiscellaneousService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.utils import get_models_and_field_types
from _main_.utils.context import Context
from _main_.utils.validator import Validator

#TODO: install middleware to catch authz violations
#TODO: add logger

class MiscellaneousHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = MiscellaneousService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/menus.list", self.navigation_menu_list()) 

  def navigation_menu_list(self) -> function:
    def navigation_menu_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      goal_info, err = self.service.navigation_menu_list(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=goal_info)
    return navigation_menu_list_view

