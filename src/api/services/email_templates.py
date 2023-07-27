from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from api.store.email_templates import EmailTemplatesStore
from _main_.utils.context import Context
from sentry_sdk import capture_message
from typing import Tuple

class EmailTemplatesService:
  """
  Service Layer for all the templates
  """

  def __init__(self):
    self.store =  EmailTemplatesStore()

  def get_email_template_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    template, err = self.store.get_email_template_info(context, args)
    if err:
      return None, err
    return serialize(template, full=True), None

  def list_email_templates(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    templates, err = self.store.list_email_templates(context, args)
    if err:
      return None, err
    return serialize_all(templates), None


  def create_email_template(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      template, err = self.store.create_email_template(context, args)
      if err:
        return None, err
      return serialize(template), None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_email_template(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    template, err = self.store.update_email_template(context, args)
    if err:
      return None, err
    return serialize(template), None
