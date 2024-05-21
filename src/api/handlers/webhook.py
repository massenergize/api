"""Handler file for all routes pertaining to summaries"""

import json
from _main_.utils.route_handler import RouteHandler
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.services.webhook import WebhookService

class WebhookHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = WebhookService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/email.bounce.webhook", self.bounce_email_webhook)
    self.add("/webhooks.inbound.get", self.process_inbound_webhook)


  def bounce_email_webhook(self, request):
    context: Context = request.context
    args: dict = json.loads(request.body.decode('utf-8'))
    res, err = self.service.bounce_email_webhook(context, args)
    if err:
      return err
    return MassenergizeResponse(data=res)


  def process_inbound_webhook(self, request):
      context: Context = request.context
      args: dict = json.loads(request.body)
      
      res, err = self.service.process_inbound_webhook(context, args)

      if err:
        return err
      return MassenergizeResponse(data=res)
