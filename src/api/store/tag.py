from _main_.utils.pagination import paginate
from database.models import Tag, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from sentry_sdk import capture_message
from typing import Tuple

class TagStore:
  def __init__(self):
    self.name = "Tag Store/DB"

  def get_tag_info(self, tag_id) -> Tuple[dict, MassEnergizeAPIError]:
    tag = Tag.objects.filter(id=tag_id)
    if not tag:
      return None, InvalidResourceError()
    return tag, None


  def list_tags(self,context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    tags = Tag.objects.filter(community__id=community_id)
    if not tags:
      return [], None
    return paginate(tags, context.args.get("page", 1), args.get("limit")), None


  def create_tag(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      new_tag = Tag.objects.objects.create(**args)
      new_tag.save()
      return new_tag, None
    except Exception:
      return None, ServerError()


  def update_tag(self, tag_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    tag = Tag.objects.filter(id=tag_id)
    if not tag:
      return None, InvalidResourceError()
    tag.update(**args)
    return tag, None


  def delete_tag(self, tag_id) -> Tuple[dict, MassEnergizeAPIError]:
    tags = Tag.objects.filter(id=tag_id)
    if not tags:
      return None, InvalidResourceError()
    tags.delete()
    return tags.first()


  def list_tags_for_community_admin(self,context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    tags =  self.list_tags_for_super_admin()

    return paginate(tags, context.args.get("page", 1), args.get("limit"))


  def list_tags_for_super_admin(self, context):
    try:
      tags = Tag.objects.all()
      return paginate(tags, context.args.get("page", 1), args.get("limit")), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
