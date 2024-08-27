from _main_.utils.metrics import timed
from database.models import Graph, UserProfile, Media, Vendor, Action, Community, Data, Tag, TagCollection, UserActionRel,RealEstateUnit, Team
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.context import Context
from django.db.models import Q, prefetch_related_objects
from api.store.team import get_team_users
from .utils import get_community_or_die, unique_media_filename
from _main_.utils.massenergize_logger import log
from typing import Tuple
from api.services.utils import send_slack_message
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL, RUN_SERVER_LOCALLY, IS_PROD, IS_CANARY
from carbon_calculator.carbonCalculator import getCarbonImpact

def get_households_engaged(community: Community):

  households_engaged = 0 if not community.goal else community.goal.attained_number_of_households
  households_engaged += (RealEstateUnit.objects.filter(community=community).count())
  actions_completed = 0 if not community.goal else community.goal.attained_number_of_actions

  done_actions = UserActionRel.objects.filter(real_estate_unit__community=community.id, status="DONE").prefetch_related('action__calculator_action')
  actions_completed += done_actions.count()
  carbon_footprint_reduction = 0 if (not community.goal or not community.goal.attained_carbon_footprint_reduction) else community.goal.attained_carbon_footprint_reduction

  # loop over actions completed
  for actionRel in done_actions:
    if actionRel.action and actionRel.action.calculator_action :
      points = getCarbonImpact(actionRel)
      carbon_footprint_reduction += points

  return {"community": {"id": community.id, "name": community.name}, 
          "actions_completed": actions_completed, "households_engaged": households_engaged, 
          "carbon_footprint_reduction": carbon_footprint_reduction}


def get_all_households_engaged():
  households_engaged = UserProfile.objects.filter(is_deleted=False, accepts_terms_and_conditions=True).count()
  done_actions = UserActionRel.objects.filter(status="DONE").prefetch_related('action__calculator_action')
  actions_completed = done_actions.count()
  carbon_footprint_reduction = 0
  for actionRel in done_actions:
    carbon_footprint_reduction += getCarbonImpact(actionRel)
  
  return {"community": {"id": 0, "name": 'Other'}, 
          "actions_completed": actions_completed, "households_engaged": households_engaged,
          "carbon_footprint_reduction": carbon_footprint_reduction}


class GraphStore:
  def __init__(self):
    self.name = "Graph Store/DB"

  def get_graph_info(self,  context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      graph = Graph.objects.filter(**args).first()
      if not graph:
        return None, InvalidResourceError()
      return graph, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_graphs(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
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
      log.exception(e)
      return None, CustomMassenergizeError(e)


  @timed
  def graph_actions_completed(self, context: Context, args) -> Tuple[Graph, MassEnergizeAPIError]:
    try:
      subdomain = args.get('subdomain', None)
      community_id = args.get('community_id', None)

      if not community_id and not subdomain:
        return None, CustomMassenergizeError("Missing community_id or subdomain field")

      community: Community = Community.objects.get(Q(pk=community_id)| Q(subdomain=subdomain))
      if not community:
        return None, InvalidResourceError()

      if not context.is_sandbox and not context.user_is_admin():
        if not community.is_published:
          return None, CustomMassenergizeError("Content Not Available Yet")

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
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def graph_actions_completed_by_team(self, context: Context, args) -> Tuple[Graph, MassEnergizeAPIError]:
    try:

      team_id = args.get('team_id', None)

      if not team_id:
        return None, CustomMassenergizeError("Missing team_id field")

      team: Team = Team.objects.get(id=team_id)

      if not team:
        return None, InvalidResourceError()

      if not context.is_sandbox and not context.user_is_admin():
        if not team.is_published:
          return None, CustomMassenergizeError("Content Not Available Yet")
  
      users = get_team_users(team)

      completed_action_rels = []
      for user in users:
        completed_action_rels.extend(user.useractionrel_set.filter(status="DONE").all())

      categories = TagCollection.objects.get(name="Category").tag_set.order_by("name").all()

      prefetch_related_objects(completed_action_rels, "action__tags")
      data = []
      for category in categories:
        data.append({
          "id"   : category.id,
          "name" : category.name,
          "value": len(list(filter(lambda action_rel : category in action_rel.action.tags.all(), completed_action_rels)))
        })

      res = {
        "data": data,
        "title": "Actions Completed By Members Of Team",
        "team": team.info()
      }
   
      return res, None
        
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)



  def graph_communities_impact(self, context: Context, args) -> Tuple[Graph, MassEnergizeAPIError]:
    try:
      subdomain = args.get('subdomain', None)
      community_id = args.get('community_id', None)
      if not community_id and not subdomain:
        return None, CustomMassenergizeError("Missing community_id or subdomain field")

      community: Community = Community.objects.get(Q(pk=community_id)| Q(subdomain=subdomain))
      if not community:
        return None, InvalidResourceError()

      res = [get_households_engaged(community)]
      limit = 10
      for c in Community.objects.filter(is_deleted=False, is_published=True)[:limit]:

        if c.id != community.id:
          res.append(get_households_engaged(c))

      return {
        "id": 1,
        "title": "Communities Impact",
        "graph_type": "bar_chart",
        "data": res
      }, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def create_graph(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
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
        image.name = unique_media_filename(image)
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
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def update_graph(self, context:Context, args:dict) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      community = get_community_or_die(context, args)
      community_goal = community.goal

      goal_updates = args.pop('goal', None)

      if goal_updates and community_goal:
          # Decision 9/2021 - Don't use initial_number_of_actions
          community_goal.initial_number_of_actions = 0
          
          target_number_of_actions = goal_updates.get('target_number_of_actions', None)
          if target_number_of_actions != None:
            community_goal.target_number_of_actions = target_number_of_actions
          

          initial_number_of_households= goal_updates.get('initial_number_of_households', None)
          if initial_number_of_households != None:
            community_goal.initial_number_of_households = initial_number_of_households
          
          target_number_of_households = goal_updates.get('target_number_of_households', None)
          if target_number_of_actions != None:
            community_goal.target_number_of_households = target_number_of_households


          initial_carbon_footprint_reduction = goal_updates.get('initial_carbon_footprint_reduction', None)
          if initial_carbon_footprint_reduction != None:
            community_goal.initial_carbon_footprint_reduction = initial_carbon_footprint_reduction
          
          target_carbon_footprint_reduction = goal_updates.get('target_carbon_footprint_reduction', None)
          if target_carbon_footprint_reduction != None:
            community_goal.target_carbon_footprint_reduction = target_carbon_footprint_reduction

          community_goal.save()


      for k,v in args.items():
        if 'reported_value' in k:
          data_id = k.split('_')[-1]
          if data_id.isnumeric() and v.isnumeric():
            data = Data.objects.filter(pk=data_id).first()
            if data:
              data.reported_value = v
              data.save()
      

      return None, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def update_data(self, context:Context, args:dict) -> Tuple[dict, MassEnergizeAPIError]:
    try:

      value = args.get('value')
      data_id = args.get('data_id')

      data = Data.objects.filter(pk=data_id).first()
      if data:

        # check for data corruption: there have been problems with data values getting clobbered
        oldvalue = data.value
        if abs(value-oldvalue)>1:
          # this is only used to increment or decrement values by one.  Something wrong here
          msg = "data.update corruption? old value %d, new value %d" % (oldvalue, value)
          raise Exception(msg)

        data.value = value
        data.save()
        return data, None


      return None, None
    except Exception as e:
      if IS_PROD or IS_CANARY:
        send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text": str(e)+str(context)}) 
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def delete_data(self, context:Context, data_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      result = Data.objects.filter(pk=data_id).delete()
      return result, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def delete_graph(self, context: Context, graph_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      graphs = Graph.objects.filter(id=graph_id)
      graphs.update(is_deleted=True, is_published=False)
      return graphs.first(), None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_graphs_for_community_admin(self,  context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
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
        comm_impact.append(get_households_engaged(c))
      comm_impact.append(get_all_households_engaged())
      return {
        "actions_completed": graphs,
        "communities_impact": comm_impact
      }, None

    except Exception as e:
      log.exception(e)
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
        comm_impact.append(get_households_engaged(c))
      comm_impact.append(get_all_households_engaged())
      return {
        "actions_completed": graphs,
        "communities_impact": comm_impact
      }, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def debug_data_fix(self) -> None:
    try:
      # attempting to fix the problem with data getting screwed up
      for community in Community.objects.all().select_related('goal'):
        if community.goal:
          action_goal= max(community.goal.target_number_of_actions, 100)
        else:
          # communities that don't have goals
          action_goal = 100

        if community.is_geographically_focused:
          user_actions = UserActionRel.objects.filter(
            real_estate_unit__community=community, status="DONE"
          )
        else:
          user_actions = UserActionRel.objects.filter(
            action__community=community, status="DONE"
          )

        for d in Data.objects.filter(community=community):
          if d and d.value>action_goal:
            oldval = d.value
            val = 0
            tag = d.tag

            for user_action in user_actions:
              if user_action.action and user_action.action.tags.filter(pk=tag.id).exists():
                val += 1

            if (val != d.value) :
              d.value = val
              d.save()
              if RUN_SERVER_LOCALLY:
                print("WARNING - data_fix: Community: " + community.name
                  + ", Category: " + tag.name
                  + ", Old: "  + str(oldval)
                  + ", New: "  + str(val))
    except:
      pass

