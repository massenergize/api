from database.models import TagCollection, UserProfile, Tag
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse

class TagCollectionStore:
  def __init__(self):
    self.name = "TagCollection Store/DB"

  def get_tag_collection_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      tag_collection_id = args.pop('tag_collection_id', None)
      if not tag_collection_id:
        return CustomMassenergizeError("Please provide a valid id")
      tag_collection = TagCollection.objects.filter(id=tag_collection_id).first()
      if not tag_collection:
        return None, InvalidResourceError()
      return tag_collection, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


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
    
    try:
      tag_collection = TagCollection.objects.filter(id=tag_collection_id).first()
      if not tag_collection:
        return None, InvalidResourceError()

      tags = Tag.objects.filter(tag_collection__id=tag_collection.id)
      name = args.pop('name', None)
      tags_to_add = args.pop('tags_to_add', '').split(', ')
      tags_to_delete = args.pop('tags_to_delete', '').split(', ')

      if name:
        tag_collection.name = name

      for (k,v) in args.items():
        if k.startswith('tag_'):
          tag_id = int(k.split('_')[-1])
          tag = tags.filter(id=tag_id).first()
          if tag:
            tag.name = v
            tag.save()

      for t in tags_to_add:
        tag = Tag.objects.create(name=t.title(), tag_collection=tag_collection)
        tag.save()

      for t in tags_to_delete:
        Tag.objects.filter(name=t.title(), tag_collection=tag_collection).delete()

      return tag_collection, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


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