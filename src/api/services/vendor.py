from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from api.store.vendor import VendorStore
from _main_.utils.context import Context
from _main_.utils.constants import ADMIN_URL_ROOT
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL, IS_PROD, IS_CANARY
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from api.utils.api_utils import get_sender_email
from api.utils.filter_functions import sort_items
from .utils import send_slack_message
from api.store.utils import get_user_or_die, get_community_or_die
from _main_.utils.massenergize_logger import log
from typing import Tuple

class VendorService:
  """
  Service Layer for all the vendors
  """

  def __init__(self):
    self.store =  VendorStore()

  def get_vendor_info(self, context, vendor_id) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.get_vendor_info(context, vendor_id)
    if err:
      return None, err
    return serialize(vendor, full=True), None

  def list_vendors(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    vendors, err = self.store.list_vendors(context, args)
    if err:
      return None, err
    return serialize_all(vendors), None


  def create_vendor(self, context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      if user_submitted:
        # this should be coming from a community site
        community = get_community_or_die(context, args)
        if not community:
          return None, CustomMassenergizeError('Vendor submission requires a community')

      vendor, err = self.store.create_vendor(context, args,user_submitted)
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
          return None, CustomMassenergizeError('Vendor submission incomplete')

        subject = 'User Service Provider Submitted'

        content_variables = {
          'name': first_name,
          'community_name': community_name,
          'url': f"{ADMIN_URL_ROOT}/admin/edit/{vendor.id}/vendor",
          'from_name': name,
          'email': email,
          'title': vendor.name,
          'body': vendor.description,
        }
        send_massenergize_rich_email(
              subject, admin_email, 'vendor_submitted_email.html', content_variables, None)

        if IS_PROD or IS_CANARY: 
          send_slack_message(
            #SLACK_COMMUNITY_ADMINS_WEBHOOK_URL, {
            SLACK_SUPER_ADMINS_WEBHOOK_URL, {
            "content": "User submitted Vendor for "+community_name,
            "from_name": name,
            "email": email,
            "subject": vendor.name,
            "message": vendor.description,
            "url": f"{ADMIN_URL_ROOT}/admin/edit/{vendor.id}/vendor",
            "community": community_name
        }) 

      return serialize(vendor), None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def update_vendor(self, context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.update_vendor(context, args, user_submitted)
    if err:
      return None, err
    return serialize(vendor), None

  def rank_vendor(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.rank_vendor(args,context)
    if err:
      return None, err
    return serialize(vendor), None


  def copy_vendor(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.copy_vendor(context, args)
    if err:
      return None, err
    return serialize(vendor), None

  def delete_vendor(self, vendor_id,context) -> Tuple[dict, MassEnergizeAPIError]:
    vendor, err = self.store.delete_vendor(vendor_id,context)
    if err:
      return None, err
    return serialize(vendor), None


  def list_vendors_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    vendors, err = self.store.list_vendors_for_community_admin(context, args)
    if err:
      return None, err
    sorted = sort_items(vendors, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_vendors_for_super_admin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    vendors, err = self.store.list_vendors_for_super_admin(context)
    if err:
      return None, err
    sorted = sort_items(vendors, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None
