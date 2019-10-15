from database.models import Community, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class CommunityStore:
  def __init__(self):
    self.name = "Community Store/DB"

  def get_community_info(self, community_id) -> (dict, MassEnergizeAPIError):
    community = Community.objects.filter(id=community_id)
    if not community:
      return None, InvalidResourceError()
    return community, None


  def list_communities(self, community_id) -> (list, MassEnergizeAPIError):
    communities = Community.objects.filter(community__id=community_id)
    if not communities:
      return [], None
    return communities, None


  def create_community(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_community = Community.create(**args)
      new_community.save()
      return new_community, None
    except Exception:
      return None, ServerError()


  def update_community(self, community_id, args) -> (dict, MassEnergizeAPIError):
    community = Community.objects.filter(id=community_id)
    if not community:
      return None, InvalidResourceError()
    community.update(**args)
    return community, None


  def delete_community(self, community_id) -> (dict, MassEnergizeAPIError):
    communities = Community.objects.filter(id=community_id)
    if not communities:
      return None, InvalidResourceError()


  def list_communities_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    communities = Community.objects.filter(community__id = community_id)
    return communities, None


  def list_communities_for_super_admin(self):
    try:
      communities = Community.objects.all()
      return communities, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))