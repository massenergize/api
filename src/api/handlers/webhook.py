"""Handler file for all routes pertaining to tags"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.services.webhook_service import WebhooksService


class WebhooksHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = WebhooksService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/webhooks.inbound.get", self.process_inbound_webhook)

  def process_inbound_webhook(self, request):
    context: Context = request.context
    args: dict = context.args
    print("==== ARGS =====", args)
    res, err = self.service.process_inbound_webhook(args)
    
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=res)

