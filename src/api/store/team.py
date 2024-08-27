from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from api.tests.common import RESET, makeUserUpload
from api.store.common import get_media_info, make_media_info
from api.utils.api_utils import get_sender_email, is_admin_of_community
from api.utils.filter_functions import get_team_member_filter_params, get_teams_filter_params
from api.utils.constants import TEAM_APPROVAL_EMAIL_TEMPLATE
from database.models import Team, UserProfile, Media, Community, TeamMember, CommunityAdminGroup, UserActionRel
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.context import Context
from _main_.utils.constants import COMMUNITY_URL_ROOT, ADMIN_URL_ROOT
from .utils import get_community_or_die, get_user_or_die, get_admin_communities, unique_media_filename
from carbon_calculator.carbonCalculator import getCarbonImpact
from _main_.utils.emailer.send_email import send_massenergize_email, send_massenergize_email_with_attachments
from typing import Tuple
from django.db.models import Q
def can_set_parent(parent, this_team=None):
  if parent.parent:
    return False
  if this_team and Team.objects.filter(parent=this_team, is_deleted=False).exists():
    return False
  return True

def get_team_users(team):
  team_users = [tm.user for tm in
                  TeamMember.objects.filter(team=team, is_deleted=False).select_related('user')]
  if team.parent:
    return team_users
  else:
    child_teams = Team.objects.filter(parent=team, is_deleted=False, is_published=True)
    child_team_users = [tm.user for tm in
                  TeamMember.objects.filter(team__in=child_teams, is_deleted=False).select_related('user')]
                  
    return set().union(team_users, child_team_users)
  

class TeamStore:
  def __init__(self):
    self.name = "Team Store/DB"

  def get_team_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      team_id = args.get("id", None)
      team = Team.objects.filter(id=team_id).first()
      if not team:
        return None, InvalidResourceError()

      userOnTeam = False
      if context.user_id:    # None for anonymous usage
        user = UserProfile.objects.get(id=context.user_id)
        userOnTeam = TeamMember.objects.filter(team=team, user=user).exists()
 
      #TODO: untested
      if not team.is_published and not (context.user_is_admin() or userOnTeam):
        return None, CustomMassenergizeError("Cannot access team until it is approved")
      return team, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def get_team_admins(self, context, team_id):
    try:
      if not team_id:
        return None, CustomMassenergizeError("provide_team_id")
      team_admins = TeamMember.objects.filter(is_admin=True, team__id=team_id, is_deleted=False)
      team_admins = [a.user for a in team_admins if a.user]
      return team_admins, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

      
  def list_teams(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      community = get_community_or_die(context, args)
      user = get_user_or_die(context, args)

      if community:
        teams = Team.objects.filter(communities__id=community.id, is_published=True, is_deleted=False)
      elif user:
        teams = user.team_set.all()
      return teams, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def team_stats(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      community = get_community_or_die(context, args)
      teams = Team.objects.filter(communities__id=community.id, is_deleted=False)

      # show unpublished teams only in sandbox.
      # TODO: Better solution would be to show also for the user who created the team, but more complicated
      if not context.is_sandbox:
        teams = teams.filter(is_published=True)

      ans = []
      for team in teams:
        res = {"members": 0, "households": 0, "actions": 0, "actions_completed": 0, "actions_todo": 0, "carbon_footprint_reduction": 0}
        res["team"] = team.simple_json()
   
        users = get_team_users(team)
        res["members"] = 0

        for user in users:
          # only include users that have joined the platform
          if user.accepts_terms_and_conditions:
            res["members"] += 1
            res["households"] += user.real_estate_units.count()
            actions = user.useractionrel_set.all()
            res["actions"] += len(actions)
            done_actions = actions.filter(status="DONE").prefetch_related('action__calculator_action')
            res["actions_completed"] += done_actions.count()
            res["actions_todo"] += actions.filter(status="TODO").count()
            for done_action in done_actions:
              if done_action.action and done_action.action.calculator_action:
                res["carbon_footprint_reduction"] += getCarbonImpact(done_action)

        ans.append(res)

      return ans, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def create_team(self, context:Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team = None
    try:
      # generally a Team will have one community, but in principle it could span multiple.  If it 
      primary_community_id = args.pop('community_id', None)
      community_ids = args.pop('communities', None)   # in case of a team spanning multiple communities

      user_email = args.pop('user_email', context.user_email)
      image_info = make_media_info(args)
      logo_file = args.pop('logo', None)

      # not used - but remove these args if present
      image_files = args.pop('pictures', None)
      video = args.pop('video', None)
  
      parent_id = args.pop('parent_id', None)
      args.pop('undefined', None)

      admin_emails = args.pop('admin_emails', [])
      
      verified_admins = []
      #verify that provided emails are valid user
      for email in admin_emails:
        admin =  UserProfile.objects.filter(email=email).first()
        if admin:
          verified_admins.append(admin)
        else:
          return None, CustomMassenergizeError(f"Email: {email} is not registered with us")
      
      if not verified_admins:
        return None, CustomMassenergizeError(f"Please provide at least one admin's email")

      community_list = []      
      if not primary_community_id:
        if community_ids:
          # if primary community id not specified, use the first one.  Ok?
          primary_community_id = community_ids[0]
        else:
          return None, CustomMassenergizeError("Please provide a primary community or communities list")

      primary_community = Community.objects.filter(pk=primary_community_id).first()
      if not primary_community:
        return None, CustomMassenergizeError("Please provide a valid community")
      args["primary_community"] = primary_community
      community_list.append(primary_community)

      if community_ids:       # the case of multiple communities
        for community_id in community_ids:
          if community_id == primary_community_id:
            continue
          community = Community.objects.filter(pk=community_id).first()
          if not community:
            return None, CustomMassenergizeError("Please provide a valid community in the list")
          community_list.append(community)
      team, _ = Team.objects.get_or_create(**args)

      # add multiple communities if that is the case (generally not)
      if community_list:
        for community in community_list:
          team.communities.add(community)

      # for the case of a sub-team, record the parent
      if parent_id:
        parent = Team.objects.filter(pk=parent_id).first()
        if parent and can_set_parent(parent):
          team.parent = parent
        else:
          return None, CustomMassenergizeError("Cannot set parent team")

      user_media_upload = None
      if logo_file: #        
        if type(logo_file) == str:
          logo_file = [logo_file]

        if type(logo_file) == list:
          # from admin portal, using media library
          logo = Media.objects.filter(pk = logo_file[0]).first()
        else:
          # from community portal, image upload
          logo_file.name = unique_media_filename(logo_file)
          logo = Media.objects.create(file=logo_file, name=f"ImageFor {team.name} Team")
        # create user media upload here 
          user_media_upload = makeUserUpload(media = logo,info=image_info, communities=[community])
  
        team.logo = logo

      user = None
      if user_email:
        user_email = user_email.strip()
        # verify that provided emails are valid user
        if not UserProfile.objects.filter(email=user_email).exists():
          return None, CustomMassenergizeError(f"Email: {user_email} is not registered with us")

        user = UserProfile.objects.filter(email=user_email).first()
        if user:
          team.user = user
          if user_media_upload:
            user_media_upload.user = user 
            user_media_upload.save()

      # TODO: this code does will not make sense when there are multiple communities for the team...
      # TODO: create a rich email template for this?
      
      # Wnen team initially created, it is not visible until reviewed by community admin
      is_published = False
      team.is_published = is_published
      if not is_published:
        cadmins = CommunityAdminGroup.objects.filter(community__id=primary_community_id).first().members.all()
        message = "A team has requested creation in your community. Visit the link below to view their information and if it is satisfactory, check the approval box and update the team.\n\n%s" % ("%s/admin/edit/%i/team" %
          (ADMIN_URL_ROOT, team.id))

        for cadmin in cadmins:
          send_massenergize_email(subject="New team awaiting approval",msg=message, to=cadmin.email,sender=None )
      team.save()

      for admin in verified_admins:
        teamMember, _ = TeamMember.objects.get_or_create(team=team,user=admin)
        teamMember.is_admin = True
        teamMember.save()

      if context.is_admin_site: 
        # ----------------------------------------------------------------
        Spy.create_team_footage(teams = [team], context = context,  type = FootageConstants.create(), notes = f"Team ID({team.id})")
        # ----------------------------------------------------------------
      return team, None
    except Exception as e:
      log.exception(e)
      if team:
        team.delete()
      return None, CustomMassenergizeError(e)


  def update_team(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      team_id = args.get('id', None)
      community_id = args.pop('community_id', None)
      subdomain = None
      if community_id:
        community = Community.objects.filter(pk=community_id).first()
        subdomain = community.subdomain

      community_ids = args.pop('communities', None)   # in case of a team spanning multiple communities

      logo = args.pop('logo', None)
      image_info = make_media_info(args)
      parent_id = args.pop('parent_id', None)
      is_published = args.pop('is_published', False)
        
      team = Team.objects.filter(id=team_id)

      # to update Team, need to be super_admin, community_admin of that community, or a team_admin
      allowed = False
      if context.user_is_super_admin:
        allowed = True
      elif context.user_is_community_admin:
        community = team.first().primary_community
        admin_communities, err = get_admin_communities(context)
        if community in admin_communities:
          allowed = True
      else:
        # user has to be on the team admin list
        teamMembers = TeamMember.objects.filter(team=team.first())
        for teamMember in teamMembers:
          teamMember_id = str(teamMember.user.id)
          if teamMember_id == context.user_id and teamMember.is_admin:
            allowed = True
            break

      if not allowed:
        return None, NotAuthorizedError()

      team.update(**args)
      team = team.first()

      if not subdomain:
        if team.primary_community:
          subdomain = team.primary_community.subdomain

      # TODO: only allow a cadmin or super admin to change this particular field?
      if is_published and not team.is_published and subdomain:

        team.is_published = True
        team_link = ("%s/%s/teams/%i") % (COMMUNITY_URL_ROOT, subdomain, team.id)
        community = team.primary_community
        message_data = {"community_name":community.name,
                  "community_logo":community.logo.file.url if community.logo and community.logo.file else None,
                  "team_name":team.name,
                  "team_logo":team.logo.file.url if team.logo and team.logo.file else None,
                  "team_link":team_link 
                  }
        
        team_admins = TeamMember.objects.filter(team=team, is_admin=True).select_related('user')
        from_email = get_sender_email(community.id)
        for team_admin in team_admins:
          send_massenergize_email_with_attachments(TEAM_APPROVAL_EMAIL_TEMPLATE, message_data,
                                                  team_admin.user.email, None, None, from_email)
      else:
        # this is how teams can get be made not live
        team.is_published = is_published

      if community_id:
        community = Community.objects.filter(pk=community_id).first()
        if community and team.primary_community != community:
            team.primary_community = community          

      if community_ids:
        for community_id in community_ids:
          community = Community.objects.filter(pk=community_id).first()
          team.communities.add(community)

      if parent_id:
          team.parent = None
          parent = Team.objects.filter(pk=parent_id).first()
          if parent and can_set_parent(parent, this_team=team):
            team.parent = parent
      else:  
          if parent_id == 0:
            team.parent = None

      if logo:
        if type(logo) == str:
          logo = [logo]     
        if type(logo) == list:
          if logo[0] == RESET: #if image is reset, delete the existing image
            team.logo = None
          else:
            # from admin portal, using media library
            logo = Media.objects.filter(pk = logo[0]).first()
            team.logo = logo
        else:
          if logo=='null':
            team.logo = None
          else:
          # from community portal, image upload
            logo.name = unique_media_filename(logo)

            logo = Media.objects.create(file=logo, name=f"ImageFor {team.name} Team")
            team.logo = logo
            makeUserUpload(media = logo, info=image_info, user = team.user, communities=[community])         

      if team.logo:
        old_image_info, can_save_info = get_media_info(team.logo)
        if can_save_info: 
          team.logo.user_upload.info.update({**old_image_info,**image_info})
          team.logo.user_upload.save()

      team.save()

      if context.is_admin_site: 
        # ----------------------------------------------------------------
        Spy.create_team_footage(teams = [team], context = context, type = FootageConstants.update(), notes = f"Team ID({team_id})")
        # ----------------------------------------------------------------
      return team, None
    except Exception as e:
      print(str(e))
      log.exception(e)
      return None, CustomMassenergizeError(e)
    

  def delete_team(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      team_id = args["id"]
      teams = Team.objects.filter(id=team_id)

      if not teams:
        return None, InvalidResourceError()
      
      #  is context user an admin of the primary community?
      if not is_admin_of_community(context, teams.first().primary_community.id):
        return None, NotAuthorizedError()
      
      team_member = TeamMember.objects.filter(team=teams.first(), user=context.user_id).first()
      
      if (not context.user_is_admin()) and (not team_member or not team_member.is_admin):
        return None, NotAuthorizedError()

      # team.members deprecated.  Delete TeamMembers separate step
      team = teams.first()
      members = TeamMember.objects.filter(team=team)
      members.delete()
      team.delete()  # or should that be team.delete()?

      if context.is_admin_site: 
        # ----------------------------------------------------------------
        Spy.create_team_footage(teams = [], context = context,  type = FootageConstants.delete(), notes=f"Deleted ID({team_id})")
        # ----------------------------------------------------------------
      return team, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def join_team(self,context, args) -> Tuple[Team, MassEnergizeAPIError]:
    try:
      team_id = args.get("id", None)
      user_id = args.get("user_id", None)
      if user_id != context.user_id:
        return None, NotAuthorizedError()

      team = Team.objects.get(id=team_id)
      user = UserProfile.objects.get(id=context.user_id)
      teamMember, created = TeamMember.objects.get_or_create(team=team, user=user)
      if created:
        teamMember.save()

      return team, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def leave_team(self, context,args) -> Tuple[Team, MassEnergizeAPIError]:
    try:
      team_id = args.get("id", None)
      user_id = args.get("user_id", None)
      team = Team.objects.get(id=team_id)
      user = UserProfile.objects.get(id=context.user_id)
      teamMember = TeamMember.objects.filter(team=team, user=user)
      if teamMember:
        teamMember.delete()
      else:
        return None, CustomMassenergizeError("User is not in that team")

      return team, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def add_team_member(self, args,context) -> Tuple[Team, MassEnergizeAPIError]:
    try:
      team_id = args.get("id", None)
      user_id = args.get("user_id", None)
      user_email = args.get("email", None)
      is_admin = args.get("is_admin", False)

      team = Team.objects.get(id=team_id)

      if not is_admin_of_community(context, team.primary_community.id):
          return None, NotAuthorizedError()

      if user_id:
        user = UserProfile.objects.get(id=user_id)
      elif user_email:
        user = UserProfile.objects.get(email=user_email)
      else:
        return None, CustomMassenergizeError("User email or id not specified")

      teamMember, created = TeamMember.objects.get_or_create(team=team, user=user)      
      teamMember.is_admin = is_admin
      teamMember.save()
      # ----------------------------------------------------------------
      Spy.create_team_footage(teams = [team], context = context, related_users = [user] if user else [],  type = FootageConstants.add(), notes=f"Added user({user.email}) to Team({team_id})")
      # ----------------------------------------------------------------
      return team, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def remove_team_member(self, args,context) -> Tuple[Team, MassEnergizeAPIError]:
    try:
      team_id = args.get('id', None)
      user_id = args.get('user_id', None)
      email = args.get('email', None)
      team = Team.objects.get(id=team_id)
      if user_id:
        user = UserProfile.objects.get(id=user_id)
      elif email:
        user = UserProfile.objects.get(email=email)

      if not is_admin_of_community(context, team.primary_community.id):
          return None, NotAuthorizedError()

      team_member = TeamMember.objects.filter(team__id=team_id, user=user)
      if team_member.count() > 0:
        team_member.delete()
      
      # ----------------------------------------------------------------
      Spy.create_team_footage(teams = [team], context = context, related_users = [user] if user else [], type = FootageConstants.remove(), notes=f"Removed user({user.email}) from team({team_id})")
      # ----------------------------------------------------------------
      return team, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def members(self, context: Context, args) -> Tuple[Team, MassEnergizeAPIError]:
    try:
      if not context.user_is_admin():
        return None, NotAuthorizedError()

      filter_params = get_team_member_filter_params(context.get_params())
      team_id = args.get('team_id', None)
      if not team_id:
        return [], CustomMassenergizeError('Please provide a valid team_id')
      
      team = Team.objects.filter(id=team_id).first()
      # for cadmins, allow only if admin of teams parent community
      if not is_admin_of_community(context, team.primary_community.id):
          return None, NotAuthorizedError()

      members = TeamMember.objects.filter(is_deleted=False, team__id=team_id, user__accepts_terms_and_conditions=True, user__is_deleted=False, *filter_params)
      return members.distinct(), None
    except Exception:
      return None, InvalidResourceError()

# shouldnt return user id (potential security issue?)
  def members_preferred_names(self, context: Context, args) -> Tuple[Team, MassEnergizeAPIError]:
    try:
      team_id = args.get('team_id', None)
      if not team_id:
        return [], CustomMassenergizeError('Please provide a valid team_id')

      team = Team.objects.filter(id=team_id).first()
      users = get_team_users(team)
      res = []
      for user in users:
        # only list users that have joined the platform
        if user.accepts_terms_and_conditions:
          member = TeamMember.objects.filter(user=user, team=team).first()
          member_obj = {
            # "id": None,
            # "user_id": str(user.id),
            "preferred_name": user.preferred_name, 
            "is_admin": False
            }
          if member:
            # member_obj['id'] = member.id 
            member_obj['is_admin'] = member.is_admin
          res.append(member_obj)

      return res, None
    except Exception as e:
      log.exception(e)
      return None, InvalidResourceError()


  def list_teams_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      team_ids = args.get("team_ids", None)

      filter_params = get_teams_filter_params(context.get_params())

      if context.user_is_super_admin:
        return self.list_teams_for_super_admin(context, args)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      
      if team_ids: 
        teams = Team.objects.filter(id__in = team_ids, *filter_params).select_related('logo', 'primary_community')
        return teams, None

      community_id = args.pop('community_id', None)
    
      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        teams = Team.objects.filter(communities__id__in = comm_ids, is_deleted=False, *filter_params).select_related('logo', 'primary_community')
        return teams.distinct(), None
      
      if not is_admin_of_community(context, community_id):
          return None, CustomMassenergizeError('You are not authorized to view members of this team')
      teams = Team.objects.filter(Q(primary_community__id=community_id,is_published=True)|Q(communities__id=community_id), is_deleted=False,*filter_params).select_related('logo', 'primary_community')   
      return teams.distinct(), None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def list_teams_for_super_admin(self, context: Context, args):
    try:
      filter_params = get_teams_filter_params(context.get_params())
  
      team_ids = args.get("team_ids", None)
      community_id = args.get("community_id")
      if team_ids: 
        teams = Team.objects.filter(id__in = team_ids, *filter_params).select_related('logo', 'primary_community')
        return teams, None
      
      if community_id:
        teams = Team.objects.filter(primary_community__id=community_id, is_published=True, is_deleted=False, *filter_params).select_related('logo', 'primary_community')
        return teams.distinct(), None

      teams = Team.objects.filter(is_deleted=False, *filter_params).select_related('logo', 'primary_community')
      return teams.distinct(), None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def list_actions_completed(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      """
      Find all the actions that members of a team have interacted with (DONE, or added to their TODO)
      Then create a summary for each of the actions: 
      i.e How many users have DONE the action or added to their TODO list 
      And the carbon_total if a user has DONE it  
      """
      team_id = args.pop("team_id", None)
      actions_completed = []
      actions_recorded = [] 
      if not team_id:
        return [], CustomMassenergizeError('Please provide a valid team_id')

      team = Team.objects.filter(id=team_id).first()
      users = get_team_users(team)

      completed_actions = UserActionRel.objects.filter(user__in=users, is_deleted=False).select_related('action', 'action__calculator_action')
      for completed_action in completed_actions:
          action_id = completed_action.action.id
          action_carbon = getCarbonImpact(completed_action)
          done = 1 if completed_action.status == "DONE" else 0
          todo = 1 if completed_action.status == "TODO" else 0
       
          #Get id of the action, if it has already been recorded, so that its fields can be updated, else, add to the array 
          ind = next((actions_completed.index(a) for a in actions_completed if a["id"]==action_id), None)
          if ind != None:
            actions_completed[ind]["done_count"] += done
            actions_completed[ind]["carbon_total"] += action_carbon
            actions_completed[ind]["todo_count"] += todo
          else:
            if action_id not in actions_recorded:
              action_name = completed_action.action.title
              category_obj = completed_action.action.tags.filter(tag_collection__name='Category').first()
              action_category = category_obj.name if category_obj else None
              actions_completed.append({"id":action_id, "name":action_name, "category":action_category, "done_count":done, "carbon_total":action_carbon, 
              "todo_count":todo, "community":{"id":completed_action.action.community.id,'subdomain':completed_action.action.community.subdomain, "name":completed_action.action.community.name}})
              actions_recorded.append(action_id)

      actions_completed = sorted(actions_completed, key=lambda d: d['done_count']*-1)
      return actions_completed, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

