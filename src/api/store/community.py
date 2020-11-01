from database.models import Community, CommunityMember, UserProfile, Action, Event, Graph, Media, ActivityLog, AboutUsPageSettings, ActionsPageSettings, ContactUsPageSettings, DonatePageSettings, HomePageSettings, ImpactPageSettings, TeamsPageSettings, Goal, CommunityAdminGroup
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from database.utils.constants import SHORT_STR_LEN
from django.db.models import Q
from .utils import get_community_or_die, get_user_or_die
import random 
from sentry_sdk import capture_message

class CommunityStore:
  def __init__(self):
    self.name = "Community Store/DB"

  def get_community_info(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      subdomain = args.get('subdomain', None)
      community_id = args.get('id', None)

      if not community_id and not subdomain:
        return None, CustomMassenergizeError("Missing community_id or subdomain field")

      community: Community = Community.objects.select_related('logo', 'goal').filter(Q(pk=community_id)| Q(subdomain=subdomain)).first()
      if not community:
        return None, InvalidResourceError()

      
      if context.is_prod and not community.is_published and not context.user_is_admin():
          return None, InvalidResourceError()

      return community, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def join_community(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      community = get_community_or_die(context, args)
      user = get_user_or_die(context, args)
      user.communities.add(community)
      user.save()

      community_member: CommunityMember = CommunityMember.objects.filter(community=community, user=user).first()
      if not community_member:
        community_member = CommunityMember.objects.create(community=community, user=user, is_admin=False)

      return user, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def leave_community(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      community = get_community_or_die(context, args)
      user = get_user_or_die(context, args)
      user.communities.remove(community)
      user.save()

      community_member: CommunityMember = CommunityMember.objects.filter(community=community, user=user).first()
      if not community_member or (not community_member.is_admin):
        community_member.delete()
     
      return user, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_communities(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      if context.is_sandbox:
        communities = Community.objects.filter(is_deleted=False, is_approved=True).exclude(subdomain='template')
      else:
        communities = Community.objects.filter(is_deleted=False, is_approved=True, is_published=True).exclude(subdomain='template')

      if not communities:
        return [], None
      return communities, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_community(self,context: Context, args) -> (dict, MassEnergizeAPIError):
    new_community = None
    try:
      logo = args.pop('logo', None)
      new_community = Community.objects.create(**args)

      have_address = args.get('is_geographically_focused', False)
      if not have_address:
        args['location'] = None
      
      if logo:
        cLogo = Media(file=logo, name=f"{args.get('name', '')} CommunityLogo")
        cLogo.save()
        new_community.logo = cLogo
      
      #create a goal for this community
      community_goal = Goal.objects.create(name=f"{new_community.name}-Goal")
      new_community.goal = community_goal
      new_community.save()

      #now create all the pages
      aboutUsPage = AboutUsPageSettings.objects.filter(is_template=True).first()
      if aboutUsPage:
        aboutUsPage.pk = None
        aboutUsPage.title = f"About {new_community.name}"
        aboutUsPage.community = new_community
        aboutUsPage.is_template = False
        aboutUsPage.save()

      actionsPage = ActionsPageSettings.objects.filter(is_template=True).first()
      if actionsPage:
        actionsPage.pk = None
        actionsPage.title = f"Actions for {new_community.name}"
        actionsPage.community = new_community
        actionsPage.is_template = False
        actionsPage.save()

      contactUsPage = ContactUsPageSettings.objects.filter(is_template=True).first()
      if contactUsPage:
        contactUsPage.pk = None 
        contactUsPage.title = f"Contact Us - {new_community.name}"
        contactUsPage.community = new_community
        contactUsPage.is_template = False
        contactUsPage.save()

      donatePage = DonatePageSettings.objects.filter(is_template=True).first()
      if donatePage:
        donatePage.pk = None 
        donatePage.title = f"Take Actions - {new_community.name}"
        donatePage.community = new_community
        donatePage.is_template = False
        donatePage.save()

      homePage = HomePageSettings.objects.filter(is_template=True).first()
      images = homePage.images.all()
      #TODO: make a copy of the images instead, then in the home page, you wont have to create new files everytime
      if homePage:
        homePage.pk = None 
        homePage.title = f"Welcome to Massenergize, {new_community.name}!"
        homePage.community = new_community
        homePage.is_template = False
        homePage.save()
        homePage.images.set(images)
    
      impactPage = ImpactPageSettings.objects.filter(is_template=True).first()
      if impactPage:
        impactPage.pk = None 
        impactPage.title = f"See our Impact - {new_community.name}"
        impactPage.community = new_community
        impactPage.is_template = False
        impactPage.save()

      # by adding TeamsPageSettings - since this doesn't exist for all communities, will it cause a problem? 
      # Create it when TeamsPageSettings in admin portal
      teamsPage = TeamsPageSettings.objects.filter(is_template=True).first()
      if teamsPage:
        teamsPage.pk = None 
        teamsPage.title = f"Teams in this community"
        teamsPage.community = new_community
        teamsPage.is_template = False
        teamsPage.save()
    
      admin_group_name  = f"{new_community.name}-{new_community.subdomain}-Admin-Group"
      comm_admin: CommunityAdminGroup = CommunityAdminGroup.objects.create(name=admin_group_name, community=new_community)
      comm_admin.save()

      if context.user_id:
        user = UserProfile.objects.filter(pk=context.user_id).first()
        if user:
          comm_admin.members.add(user)
          comm_admin.save()
     
      owner_email = args.get('owner_email', None)
      if owner_email:
        owner = UserProfile.objects.filter(email=owner_email).first()
        if owner:
          comm_admin.members.add(owner)
          comm_admin.save()

      #also clone all global actions for this community
      #global_actions = Action.objects.filter(is_global=True)
      #for action_to_copy in global_actions:
      #  print(action_to_copy)
      #  action_to_copy_id = action_to_copy.id
      #  old_tags = action_to_copy.tags.all()
      #  old_vendors = action_to_copy.vendors.all()
      #  new_action: Action = action_to_copy
      #  new_action.pk = None
      #  new_action.is_published = False
      #  new_action.is_global = False

        #make sure the action title does not exceed the max length expected
      #  suffix = f'-{new_community.subdomain}-{action_to_copy_id}'
      #  new_action.title = new_action.title[:SHORT_STR_LEN-len(suffix)]+suffix 

        # only save this action if it does not exist
        # if(Action.objects.filter(title=new_action.title, community=new_community).count() == 0):
      #  new_action.save()
      #  print(new_action.full_json())
      #  new_action.tags.set(old_tags)
      #  new_action.vendors.set(old_vendors)

      #  new_action.community = new_community
      #  new_action.save()
     
      return new_community, None
    except Exception as e:
      if new_community:
        new_community.delete()
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def update_community(self, community_id, args) -> (dict, MassEnergizeAPIError):
    try:
      logo = args.pop('logo', None)
      community = Community.objects.filter(id=community_id)
      if not community:
        return None, InvalidResourceError()
      
      if not args.get('is_geographically_focused', False):
        args['location'] = None

      community.update(**args)

      new_community = community.first()
      if logo:   
        cLogo = Media(file=logo, name=f"{args.get('name', '')} CommunityLogo")
        cLogo.save()
        new_community.logo = cLogo
        new_community.save()

      return new_community, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def delete_community(self, args) -> (dict, MassEnergizeAPIError):
    try:
      communities = Community.objects.filter(**args)
      if len(communities) > 1:
        return None, CustomMassenergizeError("You cannot delete more than one community at once")
      for c in communities:
        if "template" in c.name.lower():
          return None, CustomMassenergizeError("You cannot delete a template community")
      
      communities.delete()
      # communities.update(is_deleted=True)
      return communities, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_communities_for_community_admin(self, context: Context) -> (list, MassEnergizeAPIError):
    try:
      # if not context.user_is_community_admin and not context.user_is_community_admin:
      #   return None, CustomMassenergizeError("You are not a super admin or community admin")
      if context.user_is_community_admin:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        return [a.community for a in admin_groups], None
      elif context.user_is_super_admin:
        return self.list_communities_for_super_admin(context)
      else:
        return [], None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_communities_for_super_admin(self, context):
    try:
      # if not context.user_is_community_admin and not context.user_is_community_admin:
      #   return None, CustomMassenergizeError("You are not a super admin or community admin")

      communities = Community.objects.filter(is_deleted=False)
      return communities, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def get_graphs(self, context, community_id):
    try:
      if not community_id:
        return [], None
      graphs = Graph.objects.filter(is_deleted=False, community__id=community_id)
      return graphs, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
