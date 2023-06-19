


from database.models import CommunityAdminGroup, UserProfile


def is_admin_of_community(context, community_id):
    # super admins are admins of any community
    if context.user_is_super_admin: return True
    if not context.user_is_community_admin: return False

    user_id = context.user_id
    user_email = context.user_email
    if not community_id:
        return False
    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
    else:
        user = UserProfile.objects.filter(email=user_email).first()
    community_admins = CommunityAdminGroup.objects.filter(community__id=community_id).first()
    if not community_admins:
        return False
    is_admin = community_admins.members.filter(id=user.id).exists()
    return is_admin

def get_user_community_ids(context):
    user_id = context.user_id
    user_email = context.user_email
    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
    else:
        user = UserProfile.objects.filter(email=user_email).first()
    if not user:
        return None
    ids =  user.communityadmingroup_set.all().values_list("community__id", flat=True)
    return list(ids)
    
