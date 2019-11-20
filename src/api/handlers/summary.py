"""Handler file for all routes pertaining to summaries"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.summary import SummaryService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator


class SummaryHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = SummaryService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    #admin routes
    self.add("/summary.listForCommunityAdmin", self.community_admin_summary())
    self.add("/summary.listForSuperAdmin", self.super_admin_summary())


  def community_admin_summary(self) -> function:
    def community_admin_summary_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop("community_id", None)
      summary, err = self.service.summary_for_community_admin(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=summary)
    return community_admin_summary_view


  def super_admin_summary(self) -> function:
    def super_admin_summary_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      summary, err = self.service.summary_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=summary)
    return super_admin_summary_view