from _main_.utils.massenergize_errors import MassEnergizeAPIError
from typing import Tuple

class WebhooksService:
  def __init__(self):
   pass

  def process_inbound_webhook(self,context,  args):
    print("===== WEBHOOK ARGS =====", args)
    return {}, None

