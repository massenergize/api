from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from api.store.organization import OrganizationStore
from _main_.utils.context import Context
from _main_.utils.constants import ADMIN_URL_ROOT
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL, IS_PROD, IS_CANARY
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from api.utils.api_utils import get_sender_email
from api.utils.filter_functions import sort_items
from .utils import send_slack_message
from api.store.utils import get_user_or_die, get_community_or_die
from sentry_sdk import capture_message
from typing import Tuple

class OrganizationService:
  """
  Service Layer for all the organizations
  """

  def __init__(self):
    self.store =  OrganizationStore()

  def get_organization_info(self, context, organization_id) -> Tuple[dict, MassEnergizeAPIError]:
    organization, err = self.store.get_organization_info(context, organization_id)
    if err:
      return None, err
    return serialize(organization, full=True), None

  def list_organizations(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    organizations, err = self.store.list_organizations(context, args)
    if err:
      return None, err
    return serialize_all(organizations), None


  def create_organization(self, context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      if user_submitted:
        # this should be coming from a community site
        community = get_community_or_die(context, args)
        if not community:
          return None, CustomMassenergizeError('Organization submission requires a community')

      organization, err = self.store.create_organization(context, args,user_submitted)
      if err:
        return None, err

      if user_submitted:

        # For now, send e-mail to primary community contact for a site
        admin_email = community.owner_email
        admin_name = community.owner_name
        first_name = admin_name.split(" ")[0]
        if not first_name or first_name == "":
          first_name = admin_name

        community_name = community.name

        user = get_user_or_die(context, args)
        if user:
          name = user.full_name
          email = user.email
        else:
          return None, CustomMassenergizeError('Organization submission incomplete')

        subject = 'User Service Provider Submitted'

        content_variables = {
          'name': first_name,
          'community_name': community_name,
          'url': f"{ADMIN_URL_ROOT}/admin/edit/{organization.id}/organization",
          'from_name': name,
          'email': email,
          'title': organization.name,
          'body': organization.description,
        }
        send_massenergize_rich_email(
              subject, admin_email, 'organization_submitted_email.html', content_variables, None)

        if IS_PROD or IS_CANARY: 
          send_slack_message(
            #SLACK_COMMUNITY_ADMINS_WEBHOOK_URL, {
            SLACK_SUPER_ADMINS_WEBHOOK_URL, {
            "content": "User submitted Organization for "+community_name,
            "from_name": name,
            "email": email,
            "subject": organization.name,
            "message": organization.description,
            "url": f"{ADMIN_URL_ROOT}/admin/edit/{organization.id}/organization",
            "community": community_name
        }) 

      return serialize(organization), None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_organization(self, context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    organization, err = self.store.update_organization(context, args, user_submitted)
    if err:
      return None, err
    return serialize(organization), None

  def rank_organization(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    organization, err = self.store.rank_organization(args,context)
    if err:
      return None, err
    return serialize(organization), None


  def copy_organization(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    organization, err = self.store.copy_organization(context, args)
    if err:
      return None, err
    return serialize(organization), None

  def delete_organization(self, organization_id,context) -> Tuple[dict, MassEnergizeAPIError]:
    organization, err = self.store.delete_organization(organization_id,context)
    if err:
      return None, err
    return serialize(organization), None


  def list_organizations_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    organizations, err = self.store.list_organizations_for_community_admin(context, args)
    if err:
      return None, err
    sorted = sort_items(organizations, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_organizations_for_super_admin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    organizations, err = self.store.list_organizations_for_super_admin(context)
    if err:
      return None, err
    sorted = sort_items(organizations, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None
