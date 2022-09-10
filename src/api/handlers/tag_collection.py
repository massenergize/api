"""Handler file for all routes pertaining to tag_collections"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.tag_collection import TagCollectionService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required


class TagCollectionHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = TagCollectionService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/tag_collections.info", self.info) 
    self.add("/tag_collections.create", self.create)
    self.add("/tag_collections.add", self.create)
    self.add("/tag_collections.list", self.list)
    self.add("/tag_collections.update", self.update)
    self.add("/tag_collections.delete", self.delete)
    self.add("/tag_collections.remove", self.delete)

    #admin routes
    self.add("/tag_collections.listForCommunityAdmin", self.community_admin_list)
    self.add("/tag_collections.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_collection_info, err = self.service.get_tag_collection_info(args)
    if err:
      return err
    return MassenergizeResponse(data=tag_collection_info)

  @super_admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_collection_info, err = self.service.create_tag_collection(args)
    if err:
      return err
    return MassenergizeResponse(data=tag_collection_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_collection_info, err = self.service.list_tag_collections(context, args)
    if err:
      return err
    return MassenergizeResponse(data=tag_collection_info)

  @super_admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_collection_id = args.pop('id', None)
    if not tag_collection_id:
      return MassenergizeResponse(error="Please provide an id")
    tag_collection_info, err = self.service.update_tag_collection(tag_collection_id, args)
    if err:
      return err
    return MassenergizeResponse(data=tag_collection_info)

  @super_admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    
    tag_collection_id = args.pop('tag_collection_id', None)
    tag_collection_info, err = self.service.delete_tag_collection(tag_collection_id)
    if err:
      return err
    return MassenergizeResponse(data=tag_collection_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    tag_collections, err = self.service.list_tag_collections_for_community_admin(context,community_id)
    if err:
      return err
    return MassenergizeResponse(data=tag_collections)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    tag_collections, err = self.service.list_tag_collections_for_super_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=tag_collections)
