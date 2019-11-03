from database.models import UserProfile, CommunityAdminGroup, Community, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context

class AdminStore:
  def __init__(self):
    self.name = "Admin Store/DB"

  def add_super_admin(self, context: Context, args) -> (UserProfile, MassEnergizeAPIError):
    try:
      if not context.user_is_super_admin:
        return None, CustomMassenergizeError("You must be a super Admin to add another Super Admin")
      
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
      return None, CustomMassenergizeError(e)


  def remove_super_admin(self, context: Context, args) -> (UserProfile, MassEnergizeAPIError):
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
      print(user)
      return user, None

    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_super_admin(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      admins = UserProfile.objects.filter(is_super_admin=True)
      return admins, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def add_community_admin(self, context: Context, args) -> (UserProfile, MassEnergizeAPIError):
    try:
      if not context.user_is_super_admin and  not context.user_is_community_admin:
        return None, CustomMassenergizeError("You must be a community/super Admin to add another Super Admin")
      
      name = args.pop("name", None)
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

      if email:
        user = UserProfile.objects.filter(email=email).first()
      elif user_id:
        user = UserProfile.objects.filter(email=email).first()
      else:
        user = None

      
      if user:
        admin_group.members.add(user)
      else:
        if not admin_group.pending_admins:
          admin_group.pending_admins = {"data": [{"name": name, "email": email}]}
        else:
          data = admin_group.pending_admins.get("data", []) 
          data.append({"name": name, "email": email})
          admin_group.pending_admins = {"data": data}

      admin_group.save()
      return admin_group, None
      
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def remove_community_admin(self, context: Context, args) -> (UserProfile, MassEnergizeAPIError):
    try:
      if not context.user_is_super_admin and not context.user_is_community_admin:
        return None, CustomMassenergizeError("You must be a super Admin to add another Super Admin")
      
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

      if email:
        user = UserProfile.objects.filter(email=email).first()
      elif user_id:
        user = UserProfile.objects.filter(id=user_id).first()
      else:
        user = None

      print(admin_group.members.all())
      if user and user in admin_group.members.all():
        admin_group.members.remove(user)
        admin_group.save()
      else:
        if admin_group.pending_admins:
          data = admin_group.pending_admins.get("data", []) 
          for u in data:
            if u.get("email", None) == email:
              data.remove(u)
          admin_group.pending_admins = {"data": data}

      admin_group.save()
      return admin_group, None

    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_community_admin(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      if not context.user_is_community_admin and not context.user_is_super_admin:
        return None, CustomMassenergizeError("You must be a community admin or super admin")

      community_id = args.pop("community_id", None)
      subdomain = args.pop("subdomain", None)

      if community_id:
        community_admin_group = CommunityAdminGroup.objects.filter(community__id=community_id).first()
      elif subdomain:
        community_admin_group = CommunityAdminGroup.objects.filter(community__subdomain=subdomain).first()
      else:
        return None, CustomMassenergizeError("Please provide a community_id or subdomain")
      
      if not community_admin_group:
        if community_id:
          community = Community.objects.filter(pk=community_id).first()
        else:
          community = Community.objects.filter(subdomain=subdomain).first()


        if community:
          comm_admin = CommunityAdminGroup.objects.create(name=f"{community.name}-Admin-Group", community=community)
          comm_admin.save()          
          community_admin_group = comm_admin

        else:
          return None, CustomMassenergizeError("No community exists with that ID or subdomain")

      return community_admin_group, None
    except Exception as e:
      return None, CustomMassenergizeError(e)

