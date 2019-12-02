from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.tag_collection import TagCollectionStore
from _main_.utils.context import Context

class TagCollectionService:
  """
  Service Layer for all the tag_collections
  """

  def __init__(self):
    self.store =  TagCollectionStore()

  def get_tag_collection_info(self, tag_collection_id) -> (dict, MassEnergizeAPIError):
    tag_collection, err = self.store.get_tag_collection_info(tag_collection_id)
    if err:
      return None, err
    return serialize(tag_collection), None

  def list_tag_collections(self, tag_collection_id) -> (list, MassEnergizeAPIError):
    tag_collection, err = self.store.list_tag_collections(tag_collection_id)
    if err:
      return None, err
    return serialize_all(tag_collection), None


  def create_tag_collection(self, args) -> (dict, MassEnergizeAPIError):
    tag_collection, err = self.store.create_tag_collection(args)
    if err:
      return None, err
    return serialize(tag_collection), None


  def update_tag_collection(self,tag_collection_id, args) -> (dict, MassEnergizeAPIError):
    tag_collection, err = self.store.update_tag_collection(tag_collection_id, args)
    if err:
      return None, err
    return serialize(tag_collection), None

  def delete_tag_collection(self, tag_collection_id) -> (dict, MassEnergizeAPIError):
    tag_collection, err = self.store.delete_tag_collection(tag_collection_id)
    if err:
      return None, err
    return serialize(tag_collection), None


  def list_tag_collections_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    tag_collections, err = self.store.list_tag_collections_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(tag_collections), None


  def list_tag_collections_for_super_admin(self) -> (list, MassEnergizeAPIError):
    tag_collections, err = self.store.list_tag_collections_for_super_admin()
    if err:
      return None, err
    return serialize_all(tag_collections), None
