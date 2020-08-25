"""Handler file for all routes pertaining to tags"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.tag import TagService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator



class TagHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = TagService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/tags.info", self.info) 
    self.add("/tags.create", self.create)
    self.add("/tags.add", self.create)
    self.add("/tags.list", self.list)
    self.add("/tags.update", self.update)
    self.add("/tags.delete", self.delete)
    self.add("/tags.remove", self.delete)

    #admin routes
    self.add("/tags.listForCommunityAdmin", self.community_admin_list)
    self.add("/tags.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_info, err = self.service.get_tag_info(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tag_info)


  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_info, err = self.service.create(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tag_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    user_id = args.pop('user_id', None)
    tag_info, err = self.service.list_tags(community_id, user_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tag_info)


  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_info, err = self.service.update_tag(args.get("id", None), args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tag_info)


  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_id = args.get("id", None)
    tag_info, err = self.service.delete_tag(args.get("id", None))
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tag_info)


  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    tags, err = self.service.list_tags_for_community_admin(community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tags)


  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    tags, err = self.service.list_tags_for_super_admin()
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=tags)
