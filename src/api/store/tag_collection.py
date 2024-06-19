from api.utils.filter_functions import get_tag_collections_filter_params
from database.models import TagCollection, Tag
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError
from _main_.utils.context import Context
from sentry_sdk import capture_message
from typing import Tuple

class TagCollectionStore:
  def __init__(self):
    self.name = "TagCollection Store/DB"

  def get_tag_collection_info(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      tag_collection_id = args.pop('tag_collection_id', None)
      if not tag_collection_id:
        return CustomMassenergizeError("Please provide a valid id")
      tag_collection = TagCollection.objects.filter(id=tag_collection_id).first()
      if not tag_collection:
        return None, InvalidResourceError()
      return tag_collection, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_tag_collections(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      tag_collections = TagCollection.objects.filter(is_deleted=False)
      return tag_collections, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_tag_collection(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      name = args.pop('name', None)
      tmp_tags = args.pop('tags', '').split(',')
      new_tag_collection = TagCollection.objects.create(name=name, is_global=True)
      new_tag_collection.save()
      tags = []
      for i in range(len(tmp_tags)):
        t = tmp_tags[i]
        tag = Tag.objects.create(name=t.title(), tag_collection=new_tag_collection,rank=i+1)
        tag.save()
        # new_tag_collection.tags.add(t)

      return new_tag_collection, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def update_tag_collection(self, tag_collection_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      tag_collection = TagCollection.objects.filter(id=tag_collection_id).first()
      if not tag_collection:
        return None, InvalidResourceError()

      name = args.pop('name', None)
      if name:
        tag_collection.name = name

      rank = args.pop('rank', None)
      if rank:
        tag_collection.rank = rank

      tags = Tag.objects.filter(tag_collection=tag_collection)
      for (k,v) in args.items():
        if k.startswith('tag_') and not k.endswith('_rank'):
          tag_id = int(k.split('_')[1])
          tag = tags.filter(id=tag_id).first()
          
          if tag:
            if not tag.name.strip():
              tag.delete()
              continue

            tag.name = v.strip()
            tag.save()
        elif k.startswith('tag_') and k.endswith('_rank'):
          tag_id = int(k.split('_')[1])
          tag = tags.filter(id=tag_id).first()
          if tag:
            if not tag.name.strip():
              tag.delete()
              continue

            tag.rank = v
            tag.save()

      tags_to_add = args.pop('tags_to_add', '')
      if tags_to_add:
        tags_to_add = tags_to_add.strip().split(',')
        for i in range(len(tags_to_add)):
          t = tags_to_add[i]
          tag = Tag.objects.create(name=t.strip().title(), tag_collection=tag_collection, rank=len(tags)+i+1)
          tag.save()

      tags_to_delete = args.pop('tags_to_delete', '')
      if tags_to_delete: 
        tags_to_delete = [t.strip() for t in tags_to_delete.split(',')]
        ts = tags.filter(name__in=tags_to_delete)
        ts.delete()

      tag_collection.save()
      return tag_collection, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def delete_tag_collection(self, tag_collection_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      tag_collections = TagCollection.objects.filter(id=tag_collection_id)
      if not tag_collections:
        return None, InvalidResourceError()
      tag_collections.delete()
      return {}, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_tag_collections_for_community_admin(self, context,community_id) -> Tuple[list, MassEnergizeAPIError]:
    tag_collections = self.list_tag_collections_for_super_admin(context)
    return tag_collections


  def list_tag_collections_for_super_admin(self, context):
    try:
      filter_params = get_tag_collections_filter_params(
          context.get_params())
      tag_collections = TagCollection.objects.filter(*filter_params,is_deleted=False )
      return tag_collections, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
