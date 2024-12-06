from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from api.store.action import ActionStore
from _main_.utils.context import Context
from _main_.utils.constants import ADMIN_URL_ROOT, ME_LOGO_PNG
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL, IS_PROD, IS_CANARY
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments, send_massenergize_rich_email
from api.utils.constants import ACTION_SUBMISSION_EMAIL_TEMPLATE
from api.utils.filter_functions import sort_items
from .utils import send_slack_message
from api.store.utils import get_user_or_die
from _main_.utils.massenergize_logger import log
from typing import Tuple

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()

  def get_action_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.get_action_info(context, args)
    if err:
      return None, err
    return serialize(action, full=True), None

  def list_actions(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    actions, err = self.store.list_actions(context, args)
    if err:
      return None, err
    return serialize_all(actions), None


  def create_action(self, context: Context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      action, err = self.store.create_action(context, args, user_submitted)
      if err:
        return None, err

      if user_submitted:

        # For now, send e-mail to primary community contact for a site
        admin_email = action.community.owner_email
        admin_name = action.community.owner_name
        first_name = admin_name.split(" ")[0]
        if not first_name or first_name == "":
          first_name = admin_name

        community_name = action.community.name

        user = get_user_or_die(context, args)
        if user:
          name = user.full_name
          email = user.email
        else:
          return None, CustomMassenergizeError('Action submission incomplete')

        # subject = 'User Action Submitted'

        content_variables = {
          'name': first_name,
          'community_name': community_name,
          'url': f"{ADMIN_URL_ROOT}/admin/edit/{action.id}/action",
          'from_name': name,
          'email': email,
          'title': action.title,
          'body': action.featured_summary,
          'me_logo':ME_LOGO_PNG
        }
        # sent from MassEnergize to cadmins
        # send_massenergize_rich_email(
        #       subject, admin_email, 'action_submitted_email.html', content_variables, None)
        send_massenergize_email_with_attachments(ACTION_SUBMISSION_EMAIL_TEMPLATE, content_variables, [admin_email], None, None, None)


        if IS_PROD or IS_CANARY:
          send_slack_message(
            #SLACK_COMMUNITY_ADMINS_WEBHOOK_URL, {
            SLACK_SUPER_ADMINS_WEBHOOK_URL, {
            "content": "User submitted Action for "+community_name,
            "from_name": name,
            "email": email,
            "subject": action.title,
            "message": action.featured_summary,
            "url": f"{ADMIN_URL_ROOT}/admin/edit/{action.id}/action",
            "community": community_name,
        }) 

      return serialize(action), None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def update_action(self, context: Context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.update_action(context, args, user_submitted)
    if err:
      return None, err
    return serialize(action), None

  def rank_action(self, args, context: Context) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.rank_action(args, context)
    if err:
      return None, err
    return serialize(action), None

  def delete_action(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.delete_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def copy_action(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.copy_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def list_actions_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    actions, err = self.store.list_actions_for_community_admin(context, args)
    if err:
      return None, err
    sorted = sort_items(actions, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_actions_for_super_admin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    actions, err = self.store.list_actions_for_super_admin(context)
    if err:
      return None, err
    sorted = sort_items(actions, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None
