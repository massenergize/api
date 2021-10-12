"""Handler file for all routes pertaining to users"""
from functools import wraps
from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only, login_required
from api.services.deviceprofile import DeviceService

class DeviceHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = DeviceService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/device.info", self.info) 
    self.add("/device.create", self.create)
    self.add("/device.add", self.create)
    self.add("/device.update", self.update)
    self.add("/device.delete", self.delete)
    self.add("/device.remove", self.delete)

  def info(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", int, is_required=True)
    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    args, err = self.validator.verify(args)

    if err:
      return err

    device_info, err = self.service.get_device_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_info)

  def create(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('ip_address', int)
    self.validator.expect('device_type', int)
    self.validator.expect('operating_system', int)
    self.validator.expect("browser", list)
    self.validator.expect("visit_log", list)
    args, err = self.validator.verify(args)

    if err:
      return err
 
    device_info, err = self.service.create_device(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_info)

  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    self.validator.expect("id", int, is_required=True)
    self.validator.expect('user_profiles', int)
    self.validator.expect('ip_address', int)
    self.validator.expect('device_type', int)
    self.validator.expect('operating_system', int)
    self.validator.expect("browser", list)
    self.validator.expect("visit_log", list)
    args, err = self.validator.verify(args)

    if err:
      return err
      
    device_info, err = self.service.update_device(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_info)

  def delete(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    self.validator.expect("id", int, is_required=True)
    args, err = self.validator.verify(args)

    if err:
      return err

    device_info, err = self.service.delete_device(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_info)
