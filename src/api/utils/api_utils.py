


from database.models import CommunityAdminGroup


def is_admin_of_community(user_id, community_id):
    if not user_id or not community_id:
        return False
    community_admins = CommunityAdminGroup.objects.filter(community__id=community_id).first()
    if not community_admins:
        return False
    is_admin = community_admins.members.filter(id=user_id).exists()
    return is_admin




