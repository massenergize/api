from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from api.store.tag_collection import TagCollectionStore
from _main_.utils.context import Context
from typing import Tuple

from api.utils.filter_functions import sort_items

class TagCollectionService:
  """
  Service Layer for all the tag_collections
  """

  def __init__(self):
    self.store =  TagCollectionStore()

  def get_tag_collection_info(self, tag_collection_id) -> Tuple[dict, MassEnergizeAPIError]:
    tag_collection, err = self.store.get_tag_collection_info(tag_collection_id)
    if err:
      return None, err
    return serialize(tag_collection), None

  def list_tag_collections(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    tag_collection, err = self.store.list_tag_collections(context, args)
    if err:
      return None, err
    return serialize_all(tag_collection), None


  def create_tag_collection(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    tag_collection, err = self.store.create_tag_collection(args)
    if err:
      return None, err
    return serialize(tag_collection), None


  def update_tag_collection(self,tag_collection_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    tag_collection, err = self.store.update_tag_collection(tag_collection_id, args)
    if err:
      return None, err
    return serialize(tag_collection), None

  def delete_tag_collection(self, tag_collection_id) -> Tuple[dict, MassEnergizeAPIError]:
    tag_collection, err = self.store.delete_tag_collection(tag_collection_id)
    if err:
      return None, err
    return serialize(tag_collection), None


  def list_tag_collections_for_community_admin(self,context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    tag_collections, err = self.store.list_tag_collections_for_community_admin(context,community_id)
    if err:
      return None, err
    sorted = sort_items(tag_collections, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_tag_collections_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    tag_collections, err = self.store.list_tag_collections_for_super_admin(context)
    if err:
      return None, err
    sorted = sort_items(tag_collections, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None
