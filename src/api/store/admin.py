from _main_.utils.utils import is_not_null
from api.utils.api_utils import is_admin_of_community
from api.utils.filter_functions import get_super_admins_filter_params
from database.models import UserProfile, CommunityAdminGroup, Media, Message
from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.context import Context
from .utils import get_community, get_user, get_community_or_die, unique_media_filename
from api.store.community import CommunityStore
from _main_.utils.massenergize_logger import log
from typing import Tuple

class AdminStore:
  def __init__(self):
    self.name = "Admin Store/DB"
    self.communityStore =  CommunityStore()

  def add_super_admin(self, context: Context, args) -> Tuple[UserProfile, MassEnergizeAPIError]:
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
            
      email = args.pop("email", None)
      user_id = args.pop("user_id", None)

      if email:
        user = UserProfile.objects.filter(email=email).first()
      elif user_id:
        user = UserProfile.objects.filter(email=email).first()
      else:
        user = None
      
      if not user:
        return None, CustomMassenergizeError("The user you are trying to add does not have an account yet")
      
      user.is_super_admin = True
      user.save()
      return user, None
      
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def remove_super_admin(self, context: Context, args) -> Tuple[UserProfile, MassEnergizeAPIError]:
    try:
      if not context.user_is_super_admin:
        return None, CustomMassenergizeError("You must be a super Admin to add another Super Admin")
      
      email = args.pop("email", None)
      user_id = args.pop("user_id", None)

      if email:
        user = UserProfile.objects.filter(email=email).first()
      elif user_id:
        user = UserProfile.objects.filter(pk=user_id).first()
      else:
        user = None
      
      if not user:
        return None, CustomMassenergizeError("The user you are trying to add does not have an account yet")
      
      user.is_super_admin = False
      user.save()
      return user, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_super_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      filter_params =[]
      if args.get("params", None):
        filter_params = get_super_admins_filter_params(args.get("params"))
      admins = UserProfile.objects.filter(is_super_admin=True, is_deleted=False, *filter_params)
      return admins, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def add_community_admin(self, context: Context, args) -> Tuple[UserProfile, MassEnergizeAPIError]:
    try:
      if not context.user_is_super_admin and  not context.user_is_community_admin:
        return None, CustomMassenergizeError("You must be a community or super Admin to add another community Admin")
      
      name = args.pop("name", None)
      email = args.pop("email", None)
      user_id = args.pop("user_id", None)
      community = get_community_or_die(context, args)

      if not community:
        return None, CustomMassenergizeError("Please provide a community_id or subdomain")
      
      if not is_admin_of_community(context, community.id):
        return None, NotAuthorizedError()
      
      admin_group: CommunityAdminGroup = CommunityAdminGroup.objects.filter(community=community).first()

      if email:
        user: UserProfile = UserProfile.objects.filter(email=email).first()
      elif user_id:
        user: UserProfile = UserProfile.objects.filter(user_id=user_id).first()
      else:
        user: UserProfile = None

      if user:
        admin_group.members.add(user)
        if not user.is_super_admin and not user.is_community_admin:
          user.is_community_admin = True
          user.save()
      else:
        return None, CustomMassenergizeError("The user you are trying to add does not have an account yet")
      

      admin_group.save()

      # make sure admin is a member of the community, if not add them
      self.communityStore.join_community(context, {"community_id": community.id, "user_id":user.id})

      res = {
        "name": user.preferred_name,
        "email": user.email,
        "subdomain": community.subdomain,
        "community_name": community.name, 
        "user":user
      }

      return res, None
      
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def remove_community_admin(self, context: Context, args) -> Tuple[UserProfile, MassEnergizeAPIError]:
    try:
      if not context.user_is_super_admin and not context.user_is_community_admin:
        return None, CustomMassenergizeError("You must be a super or community Admin to remove a community Admin")
      
      email = args.pop("email", None)
      user_id = args.pop("user_id", None)
      community_id = args.pop("community_id", None)
      subdomain = args.pop("subdomain", None)

      if community_id:
        admin_group: CommunityAdminGroup = CommunityAdminGroup.objects.filter(community__id=community_id).first()
      elif subdomain:
        admin_group: CommunityAdminGroup = CommunityAdminGroup.objects.filter(community__subdomain=subdomain).first()
      else:
        return None, CustomMassenergizeError("Please provide a community_id or subdomain")
      
      if not is_admin_of_community(context, community_id):
        return None, NotAuthorizedError()

      if email:
        user = UserProfile.objects.filter(email=email).first()
      elif user_id:
        user = UserProfile.objects.filter(id=user_id).first()
      else:
        user = None

      if user and user in admin_group.members.all():
        admin_group.members.remove(user)
        admin_group.save()

        admin_at = user.communityadmingroup_set.all()
        if not (admin_at):
          # this user has been kicked off all communities they are on
          user.is_community_admin = False
          user.save()

      else:
        return None, CustomMassenergizeError("The user you are trying to remove does not exist")

        # if admin_group.pending_admins:
        #   data = admin_group.pending_admins.get("data", []) 
        #   for u in data:
        #     if u.get("email", None) == email:
        #       data.remove(u)
        #   admin_group.pending_admins = {"data": data}

      admin_group.save()
      return admin_group, None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:

      community = get_community_or_die(context, args)
      if not community:
        return None, CustomMassenergizeError("Please provide a community_id or subdomain")

      community_admin_group = CommunityAdminGroup.objects.filter(community=community).first()
      if not community_admin_group:
        if community:
          comm_admin = CommunityAdminGroup.objects.create(name=f"{community.name}-Admin-Group", community=community)
          comm_admin.save()          
          community_admin_group = comm_admin

        else:
          return None, CustomMassenergizeError("No community exists with that ID or subdomain")

      return community_admin_group, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def message_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:

      community = get_community_or_die(context, args)
      if not community:
        return None, CustomMassenergizeError("Please provide a community_id or subdomain")

      user_name = args.pop("name", None) or args.pop("user_name", None) or "Unknown user"
      title = args.pop("title", None)
      email = args.pop("email", None) or context.user_email
      body = args.pop("body", None)
      file = args.pop("uploaded_file", None)
      
      new_message = Message.objects.create(user_name=user_name, email=email, title=title, body=body, community=community)
      new_message.save()
      user, err = get_user(context.user_id, email)
      if err:
        return None, err
      if user:
        new_message.user = user
        new_message.email = user.email
        new_message.user_name = new_message.user_name or user.preferred_name
      if is_not_null(file):
        file.name = unique_media_filename(file)
        media = Media.objects.create(name=f"Messages: {new_message.title} - Uploaded File", file=file)
        media.save()
        new_message.uploaded_file = media

      new_message.save()
      return new_message, None 

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def list_admin_messages(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      
      if context.user_is_super_admin:
        return Message.objects.all(is_deleted=False), None

      community_id = args.pop('community_id', None)
      subdomain = args.pop('subdomain', None)
      community, err = get_community(community_id, subdomain)
      if err:
        return None, err

      if not community and context.user_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        messages = Message.objects.filter(community__id__in = comm_ids, is_deleted=False).select_related('uploaded_file', 'community', 'user')
        return messages, None

      elif not community:
        return [], None
      
      if not is_admin_of_community(context, community.id):
        return None, NotAuthorizedError()

      messages = Message.objects.filter(community__id = community.id, is_deleted=False).select_related('uploaded_file', 'community', 'user')
      return messages, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)