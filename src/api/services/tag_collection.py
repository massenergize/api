from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.tag_collection import TagCollectionStore

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
    return tag_collection

  def list_tag_collections(self, tag_collection_id) -> (list, MassEnergizeAPIError):
    tag_collection, err = self.store.list_tag_collections(tag_collection_id)
    if err:
      return None, err
    return tag_collection, None


  def create_tag_collection(self, args) -> (dict, MassEnergizeAPIError):
    tag_collection, err = self.store.create_tag_collection(args)
    if err:
      return None, err
    return tag_collection, None


  def update_tag_collection(self, args) -> (dict, MassEnergizeAPIError):
    tag_collection, err = self.store.update_tag_collection(args)
    if err:
      return None, err
    return tag_collection, None

  def delete_tag_collection(self, args) -> (dict, MassEnergizeAPIError):
    tag_collection, err = self.store.delete_tag_collection(args)
    if err:
      return None, err
    return tag_collection, None


  def list_tag_collections_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    tag_collections, err = self.store.list_tag_collections_for_community_admin(community_id)
    if err:
      return None, err
    return tag_collections, None


  def list_tag_collections_for_super_admin(self) -> (list, MassEnergizeAPIError):
    tag_collections, err = self.store.list_tag_collections_for_super_admin()
    if err:
      return None, err
    return tag_collections, None
