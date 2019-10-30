"""Handler file for all routes pertaining to vendors"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field, parse_bool, parse_location, parse_list
from api.services.vendor import VendorService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context

#TODO: install middleware to catch authz violations
#TODO: add logger

class VendorHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = VendorService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/vendors.info", self.info()) 
    self.add("/vendors.create", self.create())
    self.add("/vendors.add", self.create())
    self.add("/vendors.list", self.list())
    self.add("/vendors.update", self.update())
    self.add("/vendors.delete", self.delete())
    self.add("/vendors.remove", self.delete())
    self.add("/vendors.publish", self.publish())

    #admin routes
    self.add("/vendors.listForCommunityAdmin", self.community_admin_list())
    self.add("/vendors.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def vendor_info_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body()
      args = rename_field(args, 'vendor_id', 'id')
      vendor_info, err = self.service.get_vendor_info(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return vendor_info_view

  def publish(self) -> function:
    def vendor_info_view(request) -> None: 
      args = get_request_contents(request)
      args = rename_field(args, 'vendor_id', 'id')
      args['is_published'] =True
      vendor_info, err = self.service.update(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return vendor_info_view


  def create(self) -> function:
    def create_vendor_view(request) -> None: 
      args = get_request_contents(request)
      args = parse_location(args)
      args['accepted_terms_and_conditions'] = parse_bool(args.pop('accepted_terms_and_conditions', None))
      args['is_verified'] = parse_bool(args.pop('is_verified', None))
      args['communities'] = parse_list(args.pop('communities', None))
      args.pop('has_address', None)
      print(args)
      vendor_info, err = self.service.create_vendor(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return create_vendor_view


  def list(self) -> function:
    def list_vendor_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body()
      community_id = args.pop('community_id', None)
      
      vendor_info, err = self.service.list_vendors(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return list_vendor_view


  def update(self) -> function:
    def update_vendor_view(request) -> None: 
      args = get_request_contents(request)
      vendor_info, err = self.service.update_vendor(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return update_vendor_view


  def delete(self) -> function:
    def delete_vendor_view(request) -> None: 
      args = get_request_contents(request)
      vendor_id = args[id]
      vendor_info, err = self.service.delete_vendor(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return delete_vendor_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      vendors, err = self.service.list_vendors_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendors)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      vendors, err = self.service.list_vendors_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendors)
    return super_admin_list_view