"""Handler file for all routes pertaining to goals"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.misc import MiscellaneousService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.utils import get_models_and_field_types
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required

class MiscellaneousHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = MiscellaneousService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/menus.list", self.navigation_menu_list) 
    self.add("/data.backfill", self.backfill) 
    self.add("/data.carbonEquivalency.create", self.create_carbon_equivalency)
    self.add("/data.carbonEquivalency.update", self.update_carbon_equivalency)
    self.add("/data.carbonEquivalency.get", self.get_carbon_equivalencies)
    self.add("/data.carbonEquivalency.delete", self.delete_carbon_equivalency)

  def navigation_menu_list(self, request):
    context: Context = request.context
    args: dict = context.args
    goal_info, err = self.service.navigation_menu_list(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal_info)

  def backfill(self, request):
    context: Context = request.context
    args: dict = context.args
    goal_info, err = self.service.backfill(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=goal_info)

  @super_admins_only
  def create_carbon_equivalency(self, request):
    context: Context = request.context
    args: dict = context.args

    carbon_info, err = self.service.create_carbon_equivalency(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=carbon_info)

  @super_admins_only
  def update_carbon_equivalency(self, request):
    context: Context = request.context
    args: dict = context.args

    carbon_info, err = self.service.update_carbon_equivalency(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=carbon_info)

  def get_carbon_equivalencies(self, request):
    context: Context = request.context
    args: dict = context.args
    
    carbon_info, err = self.service.get_carbon_equivalencies(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=carbon_info)

  def delete_carbon_equivalency(self, request):
    context: Context = request.context
    args: dict = context.args
    
    carbon_info, err = self.service.delete_carbon_equivalency(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=carbon_info)

