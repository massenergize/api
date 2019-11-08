import logging
from _main_.utils.common import get_request_contents

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Context:
  """
  This contains info about a particular user and their request. 
  About the user:
  * Are they logged in?
  * Are they an admin? super admin? community admin?
  
  About the request:
  * args: the body/payload that was sent in the request
  * dev? : also tells you if this request is coming from one of our dev sites

  It also contains a logger
  """
  def __init__(self):
    self.args = {}
    self.is_dev = False
    self.logger = logger
    self.user_is_logged_in = False
    self.user_id = None
    self.user_email = None
    self.user_is_super_admin = False
    self.user_is_community_admin = False

  def set_user_credentials(self, decoded_token):
    self.user_is_logged_in = True
    self.user_email = decoded_token.get('email', None)
    self.user_id = decoded_token.get('user_id', None)
    self.user_is_super_admin = decoded_token.get('is_super_admin', None)
    self.user_is_community_admin = decoded_token.get('is_community_admin', None)


  def set_request_body(self, request):
    #get the request args
    self.args = get_request_contents(request)

    #set the is_dev field
    self.is_dev = self.args.pop('is_dev', False)

  def get_request_body(self):
    return self.args

  
  def user_is_admin(self):
    return self.user_is_community_admin or self.user_is_super_admin

  def __str__(self):
    return str({
      "args": self.args,
      "is_dev": self.is_dev,
      "logger": self.logger,
      "user_is_logged_in": self.user_is_logged_in,
      "user_id": self.user_id,
      "user_email": self.user_email,
      "user_is_super_admin": self.user_is_super_admin,
      "user_is_community_admin": self.user_is_community_admin,
    })







