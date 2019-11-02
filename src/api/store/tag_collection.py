from database.models import TagCollection, UserProfile, Tag
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse

class TagCollectionStore:
  def __init__(self):
    self.name = "TagCollection Store/DB"

  def get_tag_collection_info(self, tag_collection_id) -> (dict, MassEnergizeAPIError):
    tag_collection = TagCollection.objects.filter(id=tag_collection_id)
    if not tag_collection:
      return None, InvalidResourceError()
    return tag_collection, None


  def list_tag_collections(self, community_id) -> (list, MassEnergizeAPIError):
    tag_collections = TagCollection.objects.filter(community__id=community_id)
    if not tag_collections:
      return [], None
    return tag_collections, None


  def create_tag_collection(self, args) -> (dict, MassEnergizeAPIError):
    try:
      name = args.pop('name', None)
      tmp_tags = args.pop('tags', '').split(',')
      new_tag_collection = TagCollection.objects.create(name=name, is_global=True)
      new_tag_collection.save()
      tags = []
      for t in tmp_tags:
        tag = Tag.objects.create(name=t.title(), tag_collection=new_tag_collection)
        tag.save()
        # new_tag_collection.tags.add(t)

      return new_tag_collection, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_tag_collection(self, tag_collection_id, args) -> (dict, MassEnergizeAPIError):
    tag_collection = TagCollection.objects.filter(id=tag_collection_id)
    if not tag_collection:
      return None, InvalidResourceError()
    tag_collection.update(**args)
    return tag_collection, None


  def delete_tag_collection(self, tag_collection_id) -> (dict, MassEnergizeAPIError):
    tag_collections = TagCollection.objects.filter(id=tag_collection_id)
    if not tag_collections:
      return None, InvalidResourceError()


  def list_tag_collections_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    tag_collections = TagCollection.objects.filter(community__id = community_id)
    return tag_collections, None


  def list_tag_collections_for_super_admin(self):
    try:
      tag_collections = TagCollection.objects.all()
      return tag_collections, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))