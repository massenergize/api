from database.models import Testimonial, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class TestimonialStore:
  def __init__(self):
    self.name = "Testimonial Store/DB"

  def get_testimonial_info(self, testimonial_id) -> (dict, MassEnergizeAPIError):
    testimonial = Testimonial.objects.filter(id=testimonial_id)
    if not testimonial:
      return None, InvalidResourceError()
    return testimonial.full_json(), None


  def list_testimonials(self, community_id) -> (list, MassEnergizeAPIError):
    testimonials = Testimonial.objects.filter(community__id=community_id)
    if not testimonials:
      return [], None
    return [t.simple_json() for t in testimonials], None


  def create_testimonial(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_testimonial = Testimonial.create(**args)
      new_testimonial.save()
      return new_testimonial.full_json(), None
    except Exception:
      return None, ServerError()


  def update_testimonial(self, testimonial_id, args) -> (dict, MassEnergizeAPIError):
    testimonial = Testimonial.objects.filter(id=testimonial_id)
    if not testimonial:
      return None, InvalidResourceError()
    testimonial.update(**args)
    return testimonial.full_json(), None


  def delete_testimonial(self, testimonial_id) -> (dict, MassEnergizeAPIError):
    testimonials = Testimonial.objects.filter(id=testimonial_id)
    if not testimonials:
      return None, InvalidResourceError()


  def list_testimonials_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    testimonials = Testimonial.objects.filter(community__id = community_id)
    return [t.simple_json() for t in testimonials], None


  def list_testimonials_for_super_admin(self):
    try:
      testimonials = Testimonial.objects.all()
      return [t.simple_json() for t in testimonials], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))