"""Handler file for all routes pertaining to users"""
from functools import wraps
from _main_.utils.route_handler import RouteHandler
from api.services.userprofile import UserService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only, login_required

class DeviceHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = UserService()
    self.registerRoutes()

  def create(self, request):
    pass