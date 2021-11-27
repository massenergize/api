"""Handler file for all routes pertaining to users"""
from functools import wraps
from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only, login_required
from api.services.deviceprofile import DeviceService
from _main_.utils.GeoIP import GeoIP

class DeviceHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = DeviceService()
    self.registerRoutes()

    self.ipLocator = GeoIP()
  
  def __get_client_meta(self, request, args):
    meta_data = request.META

    x_forwarded_for = meta_data.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
      args["ip_address"] = x_forwarded_for.split(',')[-1]
    else:
      args["ip_address"] = request.META.get('REMOTE_ADDR')
    
    # args["lang"] = meta_data.get('LANG') # TODO: we can choose to store language
    # Example: { 'LANG': 'en_US.UTF-8' }
    # args["time_zone"] = meta_data.get('TZ') # TODO: we can choose to store language
    # Example: { 'TZ': 'UTC' }
    # args["user_agent"] = meta_data.get('HTTP_USER_AGENT') # TODO: we can choose to store language
    # args["device_type"] = meta_data.get('HTTP_USER_AGENT') # TODO: extract device type
    # args["operating_system"] = meta_data.get('HTTP_USER_AGENT') # TODO: extract OS
    # args["browser"] = meta_data.get('HTTP_USER_AGENT') # TODO: extract browser
    # Example: { 'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36' }

  def registerRoutes(self):
    self.add("/device.info", self.info) 
    self.add("/device.create", self.log_device)
    self.add("/device.add", self.log_device)
    self.add("/device.log", self.log_device)
    self.add("/device.update", self.update)
    self.add("/device.delete", self.delete)
    self.add("/device.remove", self.delete)

  def info(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    self.validator.expect("id", str, is_required=True)
    args, err = self.validator.verify(args)

    if err:
      return err

    device_info, err = self.service.get_device_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_info)

  # def create(self, request):
  #   context: Context = request.context
  #   args: dict = context.args

  #   # self.validator.expect('ip_address', str)
  #   # self.validator.expect('device_type', str)
  #   # self.validator.expect('operating_system', str)
  #   # self.validator.expect("browser", str)
  #   args, err = self.validator.verify(args)

  #   if err:
  #     return err
    
  #   self.__get_client_meta(request, args)
 
  #   device_info, err = self.service.create_device(context, args)
  #   if err:
  #     return MassenergizeResponse(error=str(err), status=err.status)
  #   return MassenergizeResponse(data=device_info)
  
  def log_device(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    self.validator.expect("id", str)
    # self.validator.expect('ip_address', str)
    args, err = self.validator.verify(args)

    if err:
      return err

    # this gets the IP address
    self.__get_client_meta(request, args)
    ip_address = args.get("ip_address", None)
    if not ip_address or ip_address in ['127.0.0.1']:
      return MassenergizeResponse(data=None)
      
    if not context.is_admin_site:
      # IP address obtained above?
      # args["ip_address"] = self.ipLocator.getIP(request)
      # args["ip_address"] = "38.242.8.93" # For testing

      location = self.ipLocator.getGeo(args["ip_address"])

      client_info = self.ipLocator.getBrowser(request)
      if not client_info:
        return MassenergizeResponse(data=None)

      device_type = client_info["device"]
      model = client_info["model"]
      args["device_type"] = f"{device_type}-{model}"
      args["operating_system"] = client_info["os"]
      args["browser"] = client_info["browser"]
      
    device, err = self.service.log_device(context, args, location)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device)
  
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    self.validator.expect("id", str, is_required=True)
    # self.validator.expect('ip_address', str)
    # self.validator.expect('device_type', str)
    # self.validator.expect('operating_system', str)
    # self.validator.expect("browser", str)
    args, err = self.validator.verify(args)

    if err:
      return err
    
    self.__get_client_meta(request, args)
      
    device_info, err = self.service.update_device(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_info)

  def delete(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    self.validator.expect("id", str, is_required=True)
    args, err = self.validator.verify(args)

    if err:
      return err

    device_info, err = self.service.delete_device(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_info)
