import logging
from _main_.utils.common import get_request_contents

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Context:
  """
  This contains info about a particular user and their session.  
  i.e. whether they are logged in or not, their user_id, 
  and also what is in the body of their request

  """
  def __init__(self):
    self.args = {}
    self.is_dev = False
    self.logger = logger("MassEnergizeLogger")
    self.user_is_logged_in = False
    self.user_id = None
    self.user_email = None
    self.user_is_super_admin = False
    self.user_is_community_admin = False

  def set_user_credentials(self, decoded_token):
    self.user_is_logged_in = True
    self.user_email = decoded_token.get('email', None)
    self.user_id = decoded_token.get('user_id', None)
    self.is_super_admin = decoded_token.get('is_super_admin', None)
    self.is_community_admin = decoded_token.get('is_community_admin', None)


  def set_args(self, request):
    self.args = get_request_contents(request)







