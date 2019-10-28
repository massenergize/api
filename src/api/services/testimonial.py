from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.testimonial import TestimonialStore

class TestimonialService:
  """
  Service Layer for all the testimonials
  """

  def __init__(self):
    self.store =  TestimonialStore()

  def get_testimonial_info(self, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.get_testimonial_info(args)
    if err:
      return None, err
    return serialize(testimonial, full=True), None

  def list_testimonials(self, args) -> (list, MassEnergizeAPIError):
    testimonial, err = self.store.list_testimonials(args)
    if err:
      return None, err
    return serialize_all(testimonial), None


  def create_testimonial(self, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.create_testimonial(args)
    if err:
      return None, err
    return serialize(testimonial), None


  def update_testimonial(self, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.update_testimonial(args)
    if err:
      return None, err
    return serialize(testimonial), None

  def delete_testimonial(self, testimonial_id) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.delete_testimonial(testimonial_id)
    if err:
      return None, err
    return serialize(testimonial), None


  def list_testimonials_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    testimonials, err = self.store.list_testimonials_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(testimonials), None


  def list_testimonials_for_super_admin(self) -> (list, MassEnergizeAPIError):
    testimonials, err = self.store.list_testimonials_for_super_admin()
    if err:
      return None, err
    return serialize_all(testimonials), None
