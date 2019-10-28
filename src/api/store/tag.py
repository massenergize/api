from database.models import Tag, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse

class TagStore:
  def __init__(self):
    self.name = "Tag Store/DB"

  def get_tag_info(self, tag_id) -> (dict, MassEnergizeAPIError):
    tag = Tag.objects.filter(id=tag_id)
    if not tag:
      return None, InvalidResourceError()
    return tag, None


  def list_tags(self, community_id) -> (list, MassEnergizeAPIError):
    tags = Tag.objects.filter(community__id=community_id)
    if not tags:
      return [], None
    return tags, None


  def create_tag(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_tag = Tag.objects.objects.create(**args)
      new_tag.save()
      return new_tag, None
    except Exception:
      return None, ServerError()


  def update_tag(self, tag_id, args) -> (dict, MassEnergizeAPIError):
    tag = Tag.objects.filter(id=tag_id)
    if not tag:
      return None, InvalidResourceError()
    tag.update(**args)
    return tag, None


  def delete_tag(self, tag_id) -> (dict, MassEnergizeAPIError):
    tags = Tag.objects.filter(id=tag_id)
    if not tags:
      return None, InvalidResourceError()


  def list_tags_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    tags = Tag.objects.filter(community__id = community_id)
    return tags, None


  def list_tags_for_super_admin(self):
    try:
      tags = Tag.objects.all()
      return tags, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))