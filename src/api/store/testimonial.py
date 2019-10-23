from database.models import Testimonial, UserProfile, Media, Vendor, Action, Community
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class TestimonialStore:
  def __init__(self):
    self.name = "Testimonial Store/DB"

  def get_testimonial_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      testimonial = Testimonial.objects.filter(**args).first()
      if not testimonial:
        return None, InvalidResourceError()
      return testimonial, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_testimonials(self, args) -> (list, MassEnergizeAPIError):
    try:
      args['is_published'] = True
      args['is_approved'] = True
      args['is_deleted'] = False
      testimonials = Testimonial.objects.filter(**args)
      if not testimonials:
        return [], None
      return testimonials, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_testimonial(self, args) -> (dict, MassEnergizeAPIError):
    try:
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      action = args.pop('action', None)
      vendor = args.pop('vendor', None)
      community = args.pop('community', None)
      user_email = args.pop('user_email', None)
     
      new_testimonial = Testimonial.objects.create(**args)

      if user_email:
        user = UserProfile.objects.filter(email=user_email).first()
        if not user:
          return None, CustomMassenergizeError("No user with that email")
        new_testimonial.user = user

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        new_testimonial.image = media

      if action:
        testimonial_action = Action.objects.get(id=action)
        new_testimonial.action = testimonial_action

      if vendor:
        testimonial_vendor = Vendor.objects.get(id=vendor)
        new_testimonial.vendor = testimonial_vendor

      if community:
        testimonial_community = Community.objects.get(id=community)
        new_testimonial.community = testimonial_community

      
      new_testimonial.save()

      # if tags:
      #   new_event.tags.set(tags)
      return new_testimonial, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_testimonial(self, testimonial_id, args) -> (dict, MassEnergizeAPIError):
    testimonial = Testimonial.objects.filter(id=testimonial_id)
    if not testimonial:
      return None, InvalidResourceError()
    testimonial.update(**args)
    return testimonial, None


  def delete_testimonial(self, testimonial_id) -> (dict, MassEnergizeAPIError):
    try:
      testimonials = Testimonial.objects.filter(id=testimonial_id)
      testimonials.update(is_deleted=True, is_published=False)
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_testimonials_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    return  Testimonial.objects.filter(community__id = community_id, is_deleted=False), None


  def list_testimonials_for_super_admin(self):
    try:
      return  Testimonial.objects.filter(is_deleted=False), None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))