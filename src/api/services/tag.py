_main_.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.tag import TagStore

class TagService:
  """
  Service Layer for all the tags
  """

  def __init__(self):
    self.store =  TagStore()

  def get_tag_info(self, tag_id) -> (dict, MassEnergizeAPIError):
    tag, err = self.store.get_tag_info(tag_id)
    if err:
      return None, err
    return serialize(tag), None

  def list_tags(self, tag_id) -> (list, MassEnergizeAPIError):
    tags, err = self.store.list_tags(tag_id)
    if err:
      return None, err
    return serialize_all(tags), None


  def create_tag(self, args) -> (dict, MassEnergizeAPIError):
    tag, err = self.store.create_tag(args)
    if err:
      return None, err
    return serialize(tag), None


  def update_tag(self, args) -> (dict, MassEnergizeAPIError):
    tag, err = self.store.update_tag(args)
    if err:
      return None, err
    return serialize(tag), None

  def delete_tag(self, args) -> (dict, MassEnergizeAPIError):
    tag, err = self.store.delete_tag(args)
    if err:
      return None, err
    return serialize(tag), None


  def list_tags_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    tags, err = self.store.list_tags_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(tags), None


  def list_tags_for_super_admin(self) -> (list, MassEnergizeAPIError):
    tags, err = self.store.list_tags_for_super_admin()
    if err:
      return None, err
    return serialize_all(tags), None
