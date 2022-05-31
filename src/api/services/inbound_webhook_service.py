from _main_.utils.massenergize_errors import MassEnergizeAPIError
from api.store.task_queue import TaskQueueStore
from _main_.utils.context import Context
from typing import Tuple


class InboundWebhookService:
  """
  Service Layer for all the inbound webhooks
  """

  def __init__(self):
    self.store = TaskQueueStore()

  def process_inbound_message(self, context: Context, args) -> Tuple[str, MassEnergizeAPIError]:
    print("======================Processing inbound message==========================")
    print("======= ARGS =========", args)
    print("======= CONTEXT =========", context)
    return "Success", None

  