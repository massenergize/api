from database.models import Graph, UserProfile, Media, Vendor, Action, Community, Data, Tag, TagCollection, UserActionRel,RealEstateUnit
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models import Q
from .utils import get_community

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
      graphs = []
      actions_completed_graph, err = self.graph_actions_completed(context, args)
      if err:
        return [], err
      communities_impact_graph, err = self.graph_communities_impact(context, args)
      if err:
        return [], err

      if actions_completed_graph:
        graphs.append(actions_completed_graph)

      if communities_impact_graph:
        graphs.append(communities_impact_graph)

      return graphs, None
    except Exception as e:
      return None, CustomMassenergizeError(e)



  def graph_actions_completed(self, context: Context, args) -> (Graph, MassEnergizeAPIError):
    try:
      subdomain = args.get('subdomain', None)
      community_id = args.get('community_id', None)

      if not community_id and not subdomain:
        return None, CustomMassenergizeError("Missing community_id or subdomain field")

      community: Community = Community.objects.get(Q(pk=community_id)| Q(subdomain=subdomain))
      if not community:
        return None, InvalidResourceError()

      if context.is_prod and not context.user_is_admin():
        if not community.is_published:
          return None, CustomMassenergizeError("Content Available Yet")

      graph = Graph.objects.prefetch_related('data').select_related('community').filter(community=community, title="Number of Actions Completed by Category").first()
      if not graph:
        graph = Graph.objects.create(community=community, title="Number of Actions Completed")
        graph.save()

      category, ok = TagCollection.objects.get_or_create(name="Category")
      for t in category.tag_set.all():
        d = Data.objects.filter(tag=t, community=community).first()
        if not d:
          d = Data.objects.create(tag=t, community=community, name=f"{t.name}", value=0)
          if not d.pk:
            d.save()
        if d.name != t.name:
          d.name = t.name
          d.save()
        graph.data.add(d)
      graph.save()

      res = graph.full_json()     
      res['community'] = community.info()
      return res, None
      
    except Exception as e:
      import traceback
      traceback.print_exc()
      return None, CustomMassenergizeError(e)


  def _get_households_engaged(self, community: Community):
    households_engaged = 0 if not community.goal else community.goal.attained_number_of_households
    households_engaged += (RealEstateUnit.objects.filter(community=community).count())
    actions_completed = 0 if not community.goal else community.goal.attained_number_of_actions
    actions_completed += UserActionRel.objects.filter(real_estate_unit__community=community.id, status="DONE").count()
    return {"community": {"id": community.id, "name": community.name}, "actions_completed": actions_completed, "households_engaged": households_engaged}


  def _get_all_households_engaged(self):
    households_engaged = UserProfile.objects.filter(is_deleted=False).count()
    actions_completed = UserActionRel.objects.filter(status="DONE").count()
    return {"community": {"id": 0, "name": 'Other'}, "actions_completed": actions_completed, "households_engaged": households_engaged}


  def graph_communities_impact(self, context: Context, args) -> (Graph, MassEnergizeAPIError):
    try:
      subdomain = args.get('subdomain', None)
      community_id = args.get('community_id', None)
      if not community_id and not subdomain:
        return None, CustomMassenergizeError("Missing community_id or subdomain field")

      community: Community = Community.objects.get(Q(pk=community_id)| Q(subdomain=subdomain))
      if not community:
        return None, InvalidResourceError()

      res = [self._get_households_engaged(community)]
      limit = 10
      for c in Community.objects.filter(is_deleted=False, is_published=True)[:limit]:

        if c.id != community.id:
          res.append(self._get_households_engaged(c))
      return {
        "id": 1,
        "title": "Communities Impact",
        "graph_type": "bar_chart",
        "data": res
      }, None
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


  def update_graph(self, context:Context, args:dict) -> (dict, MassEnergizeAPIError):
    try:
      for k,v in args.items():
        if 'reported_value' in k:
          data_id = k.split('_')[-1]
          if data_id.isnumeric() and v.isnumeric():
            data = Data.objects.filter(pk=data_id).first()
            if data:
              print(data)
              data.reported_value = v
              data.save()
      

      return None, None
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

      user = UserProfile.objects.get(pk=context.user_id)
      admin_groups = user.communityadmingroup_set.all()
      comm_ids = [ag.community.id for ag in admin_groups]
      communities = [ag.community for ag in admin_groups]

      graphs = []      
      for community in communities:
        g, err = self.graph_actions_completed(context, {"community_id": community.id})
        if g:
          graphs.append({community.name: g["data"]})

      comm_impact = []
      for c in Community.objects.filter(is_deleted=False, id__in = comm_ids):
        comm_impact.append(self._get_households_engaged(c))
      comm_impact.append(self._get_all_households_engaged())
      return {
        "actions_completed": graphs,
        "communities_impact": comm_impact
      }, None

    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_graphs_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      
      graphs = []      
      for community in Community.objects.filter(is_deleted=False)[:4]:
        g, err = self.graph_actions_completed(context, {"community_id": community.id})
        if g:
          graphs.append({community.name: g["data"]})

      comm_impact = []
      for c in Community.objects.filter(is_deleted=False)[:4]:
        comm_impact.append(self._get_households_engaged(c))
      comm_impact.append(self._get_all_households_engaged())
      return {
        "actions_completed": graphs,
        "communities_impact": comm_impact
      }, None

    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))