from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.testimonial import TestimonialStore
from _main_.utils.context import Context

class TestimonialService:
  """
  Service Layer for all the testimonials
  """

  def __init__(self):
    self.store =  TestimonialStore()

  def get_testimonial_info(self, context, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.get_testimonial_info(context, args)
    if err:
      return None, err
    return serialize(testimonial, full=True), None

  def list_testimonials(self, context, args) -> (list, MassEnergizeAPIError):
    testimonial, err = self.store.list_testimonials(context, args)
    if err:
      return None, err

    ret = serialize_all(testimonial)
    return ret, None


  def create_testimonial(self, context, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.create_testimonial(context, args)
    if err:
      return None, err
    return serialize(testimonial), None


  def update_testimonial(self, context, testimonial_id, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.update_testimonial(context, testimonial_id, args)
    if err:
      return None, err
    return serialize(testimonial), None

  def rank_testimonial(self, context, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.update_testimonial(context, args)
    if err:
      return None, err
    return serialize(testimonial), None

  def delete_testimonial(self, context, testimonial_id) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.delete_testimonial(context, testimonial_id)
    if err:
      return None, err
    return serialize(testimonial), None


  def list_testimonials_for_community_admin(self, context, community_id) -> (list, MassEnergizeAPIError):
    testimonials, err = self.store.list_testimonials_for_community_admin(context, community_id)
    if err:
      return None, err
    return serialize_all(testimonials), None


  def list_testimonials_for_super_admin(self, context) -> (list, MassEnergizeAPIError):
    testimonials, err = self.store.list_testimonials_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(testimonials), None
