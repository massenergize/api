import json
from _main_.utils.common import get_request_contents, parse_bool
from _main_.utils.constants import DEFAULT_PAGINATION_LIMIT


class Context:
  """
  This contains info about a particular user and their request. 
  About the user:
  * Are they logged in?
  * Are they an admin? super admin? community admin?
  
  About the request:
  * args: the body/payload that was sent in the request
  * dev? : also tells you if this request is coming from one of our dev sites

  """
  def __init__(self):
    self.args = {}
    self.is_dev = True
    self.is_sandbox = False
    self.is_prod = False
    self.user_is_logged_in = False
    self.user_id = None
    self.user_email = None
    self.user_is_super_admin = False
    self.user_is_community_admin = False
    self.community = None
    self.is_admin_site = False
    self.request = None
    self.preferred_language = 'en'

  def set_user_credentials(self, decoded_token):
    self.user_is_logged_in = True
    self.user_email = decoded_token.get('email', None)
    self.user_id = decoded_token.get('user_id', None)
    self.user_is_super_admin = decoded_token.get('is_super_admin', False)
    self.user_is_community_admin = decoded_token.get('is_community_admin', False)


  def set_request_body(self, request,**kwargs):
    #get the request args
    self.args = get_request_contents(request, **kwargs)
    self.request = request
    self.is_sandbox = parse_bool(self.args.pop('__is_sandbox', False))
    self.community = self.args.pop('__community', None)
    self.is_admin_site = parse_bool(self.args.pop('__is_admin_site', False))
    self.preferred_language = self.args.pop('__user_language', 'en')

    #set the is_dev field
    self.is_prod = parse_bool(self.args.pop('__is_prod', False))
    self.is_dev = not self.is_prod

  def get_request_body(self):
    return self.args

  
  def user_is_admin(self):
    return self.user_is_community_admin or self.user_is_super_admin

  def __str__(self):
    return str({
      "args": self.args,
      "is_dev": self.is_dev,
      "is_prod": self.is_prod,
      "is_sandbox": self.is_sandbox,
      "user_is_logged_in": self.user_is_logged_in,
      "user_id": self.user_id,
      "user_email": self.user_email,
      "user_is_super_admin": self.user_is_super_admin,
      "user_is_community_admin": self.user_is_community_admin,
      "preferred_language": self.preferred_language
    })


  def get_params(self):
      args = self.get_request_body()
      if args.get("params", None):
         params =json.loads(args.get('params',None))
         return params


  def get_pagination_data(self):
    args = self.get_request_body()
    limit = args.get('limit', DEFAULT_PAGINATION_LIMIT)
    next_page = args.get('page', 1)
    no_pagination = args.get('no_pagination', False)
    return {"next_page": next_page, "limit": limit, "no_pagination": no_pagination}







