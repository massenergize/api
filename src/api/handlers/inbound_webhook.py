"""Handler file for all routes pertaining to Task Queue."""

import json
from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.services.inbound_webhook_service import InboundWebhookService


class InboundWebhookHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = InboundWebhookService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/inbound.webhook.info", self.process_webhook)


  def process_webhook(self, request):
    context: Context = request.context
    args: dict = json.loads(request.body)

    team_info, err = self.service.process_inbound_message(context, args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=team_info)

  