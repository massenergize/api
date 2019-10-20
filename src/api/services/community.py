from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.community import CommunityStore
from api.utils.common import serialize, serialize_all
from api.utils.emailer.send_email import send_massenergize_rich_email
from api.utils.emailer.email_types import COMMUNITY_REGISTRATION_EMAIL

class CommunityService:
  """
  Service Layer for all the communities
  """
  

  def __init__(self):
    self.store =  CommunityStore()

  def get_community_info(self, args) -> (dict, MassEnergizeAPIError):
    community, err = self.store.get_community_info(args)
    if err:
      return None, err

    #send an email to the community admin
    return serialize(community, full=True), None

  def list_communities(self) -> (list, MassEnergizeAPIError):
    communities, err = self.store.list_communities()
    if err:
      return None, err
    return serialize_all(communities), None


  def create_community(self, args) -> (dict, MassEnergizeAPIError):
    community, err = self.store.create_community(args)
    if err:
      return None, err
    
    # send all emails
    return serialize(community), None


  def update_community(self, args) -> (dict, MassEnergizeAPIError):
    community, err = self.store.update_community(args)
    if err:
      return None, err
    return serialize(community), None

  def delete_community(self, args) -> (dict, MassEnergizeAPIError):
    community, err = self.store.delete_community(args)
    if err:
      return None, err
    return serialize(community), None


  def list_communities_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    communities, err = self.store.list_communities_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(communities), None


  def list_communities_for_super_admin(self) -> (list, MassEnergizeAPIError):
    communities, err = self.store.list_communities_for_super_admin()
    if err:
      return None, err
    return serialize_all(communities), None
