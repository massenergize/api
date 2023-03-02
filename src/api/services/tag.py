from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from api.store.tag import TagStore
from typing import Tuple

class TagService:
  """
  Service Layer for all the tags
  """

  def __init__(self):
    self.store =  TagStore()

  def get_tag_info(self, tag_id) -> Tuple[dict, MassEnergizeAPIError]:
    tag, err = self.store.get_tag_info(tag_id)
    if err:
      return None, err
    return serialize(tag), None

  def list_tags(self,context, tag_id) -> Tuple[list, MassEnergizeAPIError]:
    tags, err = self.store.list_tags(context,tag_id)
    if err:
      return None, err
    return serialize_all(tags), None


  def create_tag(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    tag, err = self.store.create_tag(args)
    if err:
      return None, err
    return serialize(tag), None


  def update_tag(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    tag, err = self.store.update_tag(args)
    if err:
      return None, err
    return serialize(tag), None

  def delete_tag(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    tag, err = self.store.delete_tag(args)
    if err:
      return None, err
    return serialize(tag), None


  def list_tags_for_community_admin(self,context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    tags, err = self.store.list_tags_for_community_admin(context,community_id)
    if err:
      return None, err
    return paginate(tags, context.get_pagination_data()), None


  def list_tags_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    tags, err = self.store.list_tags_for_super_admin(context)
    if err:
      return None, err
    return paginate(tags, context.get_pagination_data()), None
