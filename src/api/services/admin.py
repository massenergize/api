from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.admin import AdminStore
from _main_.utils.context import Context
from _main_.utils.constants import ADMIN_URL_ROOT
from _main_.utils.emailer.send_email import send_massenergize_rich_email

class AdminService:
  """
  Service Layer for all the admins
  """

  def __init__(self):
    self.store =  AdminStore()

  def add_super_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admin, err = self.store.add_super_admin(context, args)
    if err:
      return None, err
    subject = 'Welcome to the MassEnergize Team'
    content_variables = {
      'name': admin.full_name, 
      'adminlink': ADMIN_URL_ROOT,
      'admintype': 'Super',
      'admintext': "Now that you are a super admin, you have access the MassEnergize admin website at %s. You have full control over the content of our sites, can publish new communities and add new admins"%(ADMIN_URL_ROOT)
    }
    send_massenergize_rich_email(subject, admin.email, 'new_admin_email.html', content_variables)
    return serialize(admin, full=True), None


  def remove_super_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admin, err = self.store.remove_super_admin(context, args)
    if err:
      return None, err
    return serialize(admin, full=True), None


  def list_super_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admins, err = self.store.list_super_admin(context, args)
    if err:
      return None, err
    return serialize_all(admins), None


  def add_community_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admin, err = self.store.add_community_admin(context, args)
    if err:
      return None, err
    subject = 'Welcome to the MassEnergize Team'
    content_variables = {
      'name': admin.full_name, 
      'adminlink': ADMIN_URL_ROOT,
      'admintype': 'Community',
      'admintext': 'Now that you are a community admin, you have access the MassEnergize admin website at %s. You now can publish actions and events for your community. You are also in charge of finding service providers in your community and adding them to your community’s site. Just log in to your MassEnergize account on the admin site to get started.' %ADMIN_URL_ROOT
    }
    send_massenergize_rich_email(subject, admin.email, 'new_admin_email.html', content_variables)
    return serialize(admin, full=True), None


  def remove_community_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admin, err = self.store.remove_community_admin(context, args)
    if err:
      return None, err
    return serialize(admin, full=True), None


  def list_community_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admins, err = self.store.list_community_admin(context, args)
    if err:
      return None, err
    return serialize(admins), None

  def message_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    admins, err = self.store.message_admin(context, args)
    if err:
      return None, err
    #dont want to send emails all the time, just show up in the admin site and if they want they can send emails
    #need to define a send email function
    return serialize(admins), None

  def list_admin_messages(self, context, args) -> (dict, MassEnergizeAPIError):
    admins, err = self.store.list_admin_messages(context, args)
    if err:
      return None, err
    return serialize_all(admins), None

