from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.community import CommunityStore
from api.utils.emailer import send_massenergize_email

class CommunityService:
  """
  Service Layer for all the communities
  """
  

  def __init__(self):
    self.store =  CommunityStore()

  def get_community_info(self, community_id) -> (dict, MassEnergizeAPIError):
    community, err = self.store.get_community_info(community_id)
    if err:
      return None, err

    #send an email to the community admin
    return community

  def list_communities(self, community_id) -> (list, MassEnergizeAPIError):
    community, err = self.store.list_communities(community_id)
    if err:
      return None, err
    return community, None


  def create_community(self, args) -> (dict, MassEnergizeAPIError):
    community, err = self.store.create_community(args)
    if err:
      return None, err
    return community, None


  def update_community(self, args) -> (dict, MassEnergizeAPIError):
    community, err = self.store.update_community(args)
    if err:
      return None, err
    return community, None

  def delete_community(self, args) -> (dict, MassEnergizeAPIError):
    community, err = self.store.delete_community(args)
    if err:
      return None, err
    return community, None


  def list_communities_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    communities, err = self.store.list_communities_for_community_admin(community_id)
    if err:
      return None, err
    return communities, None


  def list_communities_for_super_admin(self) -> (list, MassEnergizeAPIError):
    communities, err = self.store.list_communities_for_super_admin()
    if err:
      return None, err
    return communities, None
