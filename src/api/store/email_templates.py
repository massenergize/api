
from database.models import PostmarkTemplate, PostmarkTemplate
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError
from _main_.utils.context import Context
from sentry_sdk import capture_message
from typing import Tuple

class EmailTemplatesStore:
  def __init__(self):
    self.name = "Email Templates Store/DB"

  def get_email_template_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      template_id = args.get("id", None)
      template = PostmarkTemplate.objects.filter(id=template_id).first()

      if not template:
        return None, InvalidResourceError()
      return template, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_email_templates(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      templates = PostmarkTemplate.objects.filter(is_deleted=False, **args)

      return templates, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_email_template(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      name = args.get("name", None)
      template_id = args.get('template_id', [])

      templates = PostmarkTemplate.objects.filter(name=name, template_id=template_id, is_deleted=False)
      if templates:
        return templates.first(), None

      new_template = PostmarkTemplate.objects.create(**args)

      
      # ----------------------------------------------------------------
    #   Spy.create_email_template_footage(actions = [new_email_template_], context = context, actor = new_email_template_.user, type = FootageConstants.create(), notes = f"PostmarkTemplate ID({new_email_template_.id})")
      # ----------------------------------------------------------------
      return new_template, None 

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_email_template(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      template_id = args.get('id', None)
      templates = PostmarkTemplate.objects.filter(id=template_id)
      if not templates:
        return None, InvalidResourceError()
      templates.update(**args)

      # ----------------------------------------------------------------
    #   Spy.create_email_template_footage(templates = [template], context = context, type = FootageConstants.update(), notes =f"PostmarkTemplate ID({template_id})")
      # ----------------------------------------------------------------
      return templates.first(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)




