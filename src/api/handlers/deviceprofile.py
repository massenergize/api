"""Handler file for all routes pertaining to users"""
from functools import wraps
from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only, login_required
from api.src.api.services.deviceprofile import DeviceProfileService

class DeviceProfileHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = DeviceProfileService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/device_profiles.info", self.info) 
    self.add("/device_profiles.create", self.create)
    self.add("/device_profiles.add", self.create)
    self.add("/device_profiles.update", self.update)
    self.add("/device_profiles.delete", self.delete)
    self.add("/device_profiles.remove", self.delete)

  def info(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", int, is_required=True)
    self.validator.rename("device_profile_id", "id")
    self.validator.rename("device_id", "id")
    args, err = self.validator.verify(args)

    if err:
      return err

    device_profile_info, err = self.service.get_device_profile_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_profile_info)

  def create(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('ip_address', int)
    self.validator.expect('device_type', int)
    self.validator.expect('operating_system', int)
    self.validator.expect("browser", list)
    args, err = self.validator.verify(args)

    if err:
      return err
 
    device_profile_info, err = self.service.create_device_profile(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_profile_info)

  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", int, is_required=True)
    self.validator.rename("device_profile_id", "id")
    self.validator.rename("device_id", "id")
    self.validator.expect('user_profiles', int)
    self.validator.expect('ip_address', int)
    self.validator.expect('device_type', int)
    self.validator.expect('operating_system', int)
    self.validator.expect("browser", list)
    self.validator.expect("visit_log", list)
    args, err = self.validator.verify(args)

    if err:
      return err
      
    device_profile_info, err = self.service.update_device_profile(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_profile_info)

  def delete(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", int, is_required=True)
    self.validator.rename("device_profile_id", "id")
    self.validator.rename("device_id", "id")
    args, err = self.validator.verify(args)

    if err:
      return err

    device_profile_id = args.pop('device_profile_id', None)

    device_profile_info, err = self.service.delete_device_profile(context, device_profile_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_profile_info)
