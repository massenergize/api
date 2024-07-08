from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.constants import ADMIN_URL_ROOT
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL, IS_PROD, IS_CANARY
from _main_.utils.common import serialize, serialize_all
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from _main_.utils.pagination import paginate
from api.utils.api_utils import get_sender_email
from api.utils.filter_functions import sort_items
from .utils import send_slack_message
from api.store.testimonial import TestimonialStore
from _main_.utils.massenergize_logger import log
from typing import Tuple

class TestimonialService:
  """
  Service Layer for all the testimonials
  """
  
  def __init__(self):
    self.store =  TestimonialStore()

  def get_testimonial_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    testimonial, err = self.store.get_testimonial_info(context, args)
    if err:
      return None, err
    return serialize(testimonial, full=True), None

  def list_testimonials(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    testimonials, err = self.store.list_testimonials(context, args)
    if err:
      return None, err
    return serialize_all(testimonials), None


  def create_testimonial(self, context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      testimonial, err = self.store.create_testimonial(context, args)
      if err:
        return None, err

      if user_submitted:

        # For now, send e-mail to primary community contact for a site
        admin_email = testimonial.community.owner_email
        admin_name = testimonial.community.owner_name
        first_name = admin_name.split(" ")[0]
        if not first_name or first_name == "":
          first_name = admin_name

        community_name = testimonial.community.name
        user = testimonial.user
        if user:
          name = user.full_name
          email = user.email
        else:
          return None, CustomMassenergizeError('Testimonial submission incomplete')

        subject = 'User Testimonial Submitted'

        content_variables = {
          'name': first_name,
          'community_name': community_name,
          'url': f"{ADMIN_URL_ROOT}/admin/edit/{testimonial.id}/testimonial",
          'from_name': name,
          'email': email,
          'title': testimonial.title,
          'body': testimonial.body,
        }
        send_massenergize_rich_email(
              subject, admin_email, 'testimonial_submitted_email.html', content_variables, None)

        if IS_PROD or IS_CANARY:
          send_slack_message(
            #SLACK_COMMUNITY_ADMINS_WEBHOOK_URL, {
            SLACK_SUPER_ADMINS_WEBHOOK_URL, {
            "content": "User submitted Testimonial for "+community_name,
            "from_name": name,
            "email": email,
            "subject": testimonial.title,
            "message": testimonial.body,
            "url": f"{ADMIN_URL_ROOT}/admin/edit/{testimonial.id}/testimonial",
            "community": community_name
        }) 

      return serialize(testimonial), None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def update_testimonial(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    testimonial, err = self.store.update_testimonial(context, args)
    if err:
      return None, err
    return serialize(testimonial), None

  def rank_testimonial(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    testimonial, err = self.store.rank_testimonial(args,context)
    if err:
      return None, err
    return serialize(testimonial), None

  def delete_testimonial(self, context, testimonial_id) -> Tuple[dict, MassEnergizeAPIError]:
    testimonial, err = self.store.delete_testimonial(context, testimonial_id)
    if err:
      return None, err
    return serialize(testimonial), None


  def list_testimonials_for_community_admin(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    testimonials, err = self.store.list_testimonials_for_community_admin(context, args)
    if err:
      return None, err
    sorted = sort_items(testimonials, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_testimonials_for_super_admin(self, context,args) -> Tuple[list, MassEnergizeAPIError]:
    testimonials, err = self.store.list_testimonials_for_super_admin(context,args)
    if err:
      return None, err
    sorted = sort_items(testimonials, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None
