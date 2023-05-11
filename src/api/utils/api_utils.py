


from database.models import CommunityAdminGroup, UserProfile


def is_admin_of_community(user_id, community_id):
    if not user_id or not community_id:
        return False
    community_admins = CommunityAdminGroup.objects.filter(community__id=community_id).first()
    if not community_admins:
        return False
    is_admin = community_admins.members.filter(id=user_id).exists()
    return is_admin





def get_user_community_ids(context):
    print("=====ctx=====",context)
    user_id = context.user_id
    user_email = context.email
    if context.user_is:
        user = UserProfile.objects.filter(id=user_id).first()
    else:
        user = UserProfile.objects.filter(email=user_email).first()
    print("== user ==", user)
    if not user:
        return None
    ids =  user.communityadmingroup_set.all().values_list("community__id", flat=True)
    print("-==== ids in FUNC====", ids)
    return list(ids)
    
