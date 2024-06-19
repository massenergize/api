"""Handler file for all routes pertaining to summaries"""

import json
import logging

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
    
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError as json_error:
            logging.error(f'Failed to parse request body as JSON: {json_error}')
            return MassenergizeResponse(error=str(json_error))
    
        try:
            response_data, error = self.service.bounce_email_webhook(context, request_data)
    
            if error:
                logging.error(f'Error processing bounce email webhook: {error}')
                return error
    
            return MassenergizeResponse(data=response_data)
    
        except Exception as unexpected_error:
            logging.error(f'Unexpected error processing bounce email webhook: {unexpected_error}')
            return MassenergizeResponse(error=str(unexpected_error))
    
    def process_inbound_webhook(self, request):
        context: Context = request.context
    
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError as json_error:
            logging.error(f'Failed to parse request body as JSON: {json_error}')
            return MassenergizeResponse(error=str(json_error))
    
        try:
            response_data, error = self.service.process_inbound_webhook(context, request_data)
    
            if error:
                logging.error(f'Error processing inbound webhook: {error}')
                return error
    
            return MassenergizeResponse(data=response_data)
    
        except Exception as unexpected_error:
            logging.error(f'Unexpected error processing inbound webhook: {unexpected_error}')
            return MassenergizeResponse(error=str(unexpected_error))
