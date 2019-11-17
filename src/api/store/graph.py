from database.models import Graph, UserProfile, Media, Vendor, Action, Community, Tag
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models import Q

class GraphStore:
  def __init__(self):
    self.name = "Graph Store/DB"

  def get_graph_info(self,  context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      graph = Graph.objects.filter(**args).first()
      if not graph:
        return None, InvalidResourceError()
      return graph, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_graphs(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      subdomain = args.pop('subdomain', None)
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      user_email = args.pop('user_email', None)

      graphs = []

      if context.is_dev:
        if subdomain:
          graphs = Graph.objects.filter(community__subdomain=subdomain, is_deleted=False)
        elif community_id:
          graphs = Graph.objects.filter(community__id=community_id, is_deleted=False)
        elif user_id:
          graphs = Graph.objects.filter(user__id=user_id, is_deleted=False)
        elif user_email:
          graphs = Graph.objects.filter(user__email=subdomain, is_deleted=False)

      else:
        if subdomain:
          graphs = Graph.objects.filter(community__subdomain=subdomain, is_deleted=False, is_published=True)
        elif community_id:
          graphs = Graph.objects.filter(community__id=community_id, is_deleted=False, is_published=True)
        elif user_id:
          graphs = Graph.objects.filter(user__id=user_id, is_deleted=False, is_published=True)
        elif user_email:
          graphs = Graph.objects.filter(user__email=subdomain, is_deleted=False, is_published=True)


      return graphs, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_graph(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      action = args.pop('action', None)
      vendor = args.pop('vendor', None)
      community = args.pop('community', None)
      user_email = args.pop('user_email', None)
     
      new_graph = Graph.objects.create(**args)

      if user_email:
        user = UserProfile.objects.filter(email=user_email).first()
        if user:
          new_graph.user = user

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        new_graph.image = media

      if action:
        graph_action = Action.objects.get(id=action)
        new_graph.action = graph_action

      if vendor:
        graph_vendor = Vendor.objects.get(id=vendor)
        new_graph.vendor = graph_vendor

      if community:
        graph_community = Community.objects.get(id=community)
        new_graph.community = graph_community

      
      new_graph.save()

      tags_to_set = []
      for t in tags:
        tag = Tag.objects.filter(pk=t).first()
        if tag:
          tags_to_set.append(tag)
      if tags_to_set:
        new_graph.tags.set(tags_to_set)
    
      return new_graph, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_graph(self, context: Context, graph_id, args) -> (dict, MassEnergizeAPIError):
    try:
      graph = Graph.objects.filter(id=graph_id)
      if not graph:
        return None, InvalidResourceError()
      
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      action = args.pop('action', None)
      vendor = args.pop('vendor', None)
      community = args.pop('community', None)
      user_email = args.pop('user_email', None)
     
      new_graph = graph.first()

      # if user_email:
      #   user = UserProfile.objects.filter(email=user_email).first()
      #   if not user:
      #     return None, CustomMassenergizeError("No user with that email")
      #   new_graph.user = user

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        new_graph.image = media

      if action:
        graph_action = Action.objects.get(id=action)
        new_graph.action = graph_action

      if vendor:
        graph_vendor = Vendor.objects.get(id=vendor)
        new_graph.vendor = graph_vendor

      if community:
        graph_community = Community.objects.get(id=community)
        new_graph.community = graph_community
      
      tags_to_set = []
      for t in tags:
        tag = Tag.objects.filter(pk=t).first()
        if tag:
          tags_to_set.append(tag)
      if tags_to_set:
        new_graph.tags.set(tags_to_set)

      new_graph.save()
      graph.update(**args)
      return new_graph, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def delete_graph(self, context: Context, graph_id) -> (dict, MassEnergizeAPIError):
    try:
      graphs = Graph.objects.filter(id=graph_id)
      graphs.update(is_deleted=True, is_published=False)
      return graphs.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_graphs_for_community_admin(self,  context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_graphs_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        graphs = Graph.objects.filter(community__id__in = comm_ids, is_deleted=False).select_related('image', 'community').prefetch_related('tags')
        return graphs, None

      graphs = Graph.objects.filter(community__id = community_id, is_deleted=False).select_related('image', 'community').prefetch_related('tags')
      return graphs, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def list_graphs_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      events = Graph.objects.filter(is_deleted=False).select_related('image', 'community', 'vendor').prefetch_related('tags')
      return events, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))