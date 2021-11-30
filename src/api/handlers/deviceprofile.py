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
  
  def registerRoutes(self):
    self.add("/device.info", self.info) 
    self.add("/device.create", self.log_device)
    self.add("/device.add", self.log_device)
    self.add("/device.log", self.log_device)
    self.add("/device.pmetrics", self.platform_metrics)
    self.add("/device.cmetrics", self.community_metrics)
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
  
  def log_device(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    self.validator.expect("id", str)
    args, err = self.validator.verify(args)

    if err:
      return err

    if not context.is_admin_site:
      args["ip_address"] = self.ipLocator.getIP(request)
      # args["ip_address"] = "38.242.8.93" # For testing

      location = self.ipLocator.getGeo(args["ip_address"])

      client_info = self.ipLocator.getBrowser(request)
      device_type = client_info["device"]
      model = client_info["model"]
      args["device_type"] = f"{device_type}-{model}"
      args["operating_system"] = client_info["os"]
      args["browser"] = client_info["browser"]
      
    device, err = self.service.log_device(context, args, location)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device)

  @super_admins_only
  def platform_metrics(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("metric", str, is_required=True)
    self.validator.expect("community_id", str)
    args, err = self.validator.verify(args)

    if err:
      return err

    metric = args.get("metric", None)
    community_id = args.get("community_id", None)
    
    if metric is "anonymous_users":
      metric, err = self.service.metric_anonymous_users(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)

    if metric is "anonymous_community_users":
      metric, err = self.service.metric_anonymous_community_users(context, args, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)

    if metric is "user_profiles":
      metric, err = self.service.metric_user_profiles(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)

    if metric is "community_profiles":
      metric, err = self.service.metric_community_profiles(context, args, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
        
    return MassenergizeResponse(data=metric)
  
  @admins_only
  def community_metrics(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("metric", str, is_required=True)
    self.validator.expect("community_id", str)
    args, err = self.validator.verify(args)

    if err:
      return err
    
    metric = args["metric"] if "metric" in args else None
    community_id = args["community_id"] if "community_id" in args else None
    
    if metric is "anonymous_community_users" and community_id:
      metric, err = self.service.metric_anonymous_community_users(context, args, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
    
    if metric is "community_profiles" and community_id:
      metric, err = self.service.metric_community_profiles(context, args, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)

    if metric is "community_profiles_over_time" and community_id:
      metric, err = self.service.metric_community_profiles_over_time(context, args, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
    
    return MassenergizeResponse(data=metric)
  
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.rename("device_id", "id")
    self.validator.rename("device_profile_id", "id")
    self.validator.expect("id", str, is_required=True)
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
    self.validator.expect("id", str, is_required=True)
    args, err = self.validator.verify(args)

    if err:
      return err

    device_info, err = self.service.delete_device(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=device_info)
