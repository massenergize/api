from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from api.store.userprofile import UserStore
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from _main_.utils.constants import COMMUNITY_URL_ROOT
import os, csv
import re

def _parse_import_file(csvfile):
  """
  Helper function used to parse csv import file 
  """
  try:    
    # csv_ref is a bytes object, we need a csv
    # so we copy it as a csv temporarily to the disk
    temporarylocation="testout.csv"
    with open(temporarylocation, 'wb') as out:
      var = csvfile.read()
      out.write(var)
    # filecontents is a list of dictionaries, with each list item representing a row in the CSV
    filecontents = []
    with open(temporarylocation, "r") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
          filecontents.append(row)
    # and then delete it once we are done parsing it    
    os.remove(temporarylocation)
  except Exception as e:
    err = str(e)
    return None, err
  return filecontents, None

def _send_invitation_email(user_info, mess):
  # TODO: include community logo

  # send email inviting user to complete their profile
  cadmin_name = user_info.get("cadmin", "The Community Administrator")
  community_name = user_info.get("community", None)
  team_name = user_info.get("team", None)
  subdomain = user_info.get("subdomain", "global")
  email = user_info.get("email", None)

  message = cadmin_name + " invited you to join the following MassEnergize Community: " + community_name + "\n"

  if mess and mess != "":
      message += "They have included a message for you here:\n"
      message += "\n" + mess + "\n"

  if team_name:
    message += "You have also been assigned to the following team: " + team_name + "\n"

  link = f'{COMMUNITY_URL_ROOT}/{subdomain}' + "/signup"
  message += "Use the following link to join " + community_name + ": " + link
  subject = cadmin_name + " invited you to join a MassEnergize Community"
  send_massenergize_email(subject=subject , msg=message, to=email)

class UserService:
  """
  Service Layer for all the users
  """

  def __init__(self):
    self.store =  UserStore()

  def get_user_info(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.get_user_info(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None

  def add_household(self,context: Context, args) -> (dict, MassEnergizeAPIError):
    household, err = self.store.add_household(context, args)
    if err:
      return None, err
    return serialize(household, full=True), None

  def edit_household(self,context: Context, args) -> (dict, MassEnergizeAPIError):
    household, err = self.store.edit_household(context, args)
    if err:
      return None, err
    return serialize(household, full=True), None

  def remove_household(self,context: Context, args) -> (dict, MassEnergizeAPIError):
    household, err = self.store.remove_household(context, args)
    if err:
      return None, err
    return household, None

  def list_users(self, community_id) -> (list, MassEnergizeAPIError):
    user, err = self.store.list_users(community_id)
    if err:
      return None, err
    return serialize_all(user), None


  def list_actions_todo(self, context: Context, args) -> (list, MassEnergizeAPIError):
    actions_todo, err = self.store.list_todo_actions(context, args)
    if err:
      return None, err
    return serialize_all(actions_todo), None

  def list_actions_completed(self, context: Context, args) -> (list, MassEnergizeAPIError):
    actions_completed, err = self.store.list_completed_actions(context, args)
    if err:
      return None, err
    return serialize_all(actions_completed), None

  def remove_user_action(self, context: Context, user_action_id) -> (list, MassEnergizeAPIError):
    result, err = self.store.remove_user_action(context, user_action_id)
    if err:
      return None, err
    return result, None

  def list_events_for_user(self, context: Context, args) -> (list, MassEnergizeAPIError):
    events, err = self.store.list_events_for_user(context, args)
    if err:
      return None, err
    return serialize_all(events), None

  def check_user_imported(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    imported_info, err = self.store.check_user_imported(context, args)
    if err:
      return None, err
    return imported_info, None
  
  def complete_imported_user(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    imported_info, err = self.store.complete_imported_user(context, args)
    if err:
      return None, err
    return imported_info, None

  def create_user(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    res, err = self.store.create_user(context, args)
    if err:
      return None, err
    
    community = res["community"]
    user = res["user"]
    community_name =  community.name if community else "Global Massenergize Community"
    community_logo =  community.logo.file.url if community and community.logo else 'https://s3.us-east-2.amazonaws.com/community.massenergize.org/static/media/logo.ee45265d.png'
    subdomain =   community.subdomain if community else "global"
    subject = f'Welcome to {community_name}, a MassEnergize community'
    homelink = f'{COMMUNITY_URL_ROOT}/{subdomain}'
    
    content_variables = {
      'name': user.preferred_name,
      'community': community_name,
      'homelink': homelink,
      'logo': community_logo,
      'actionslink':f'{homelink}/actions',
      'eventslink':f'{homelink}/events',
      'serviceslink': f'{homelink}/services',
      'privacylink': f"{homelink}/policies?name=Privacy%20Policy"
      }
    
    send_massenergize_rich_email(subject, user.email, 'user_registration_email.html', content_variables)

    return serialize(user, full=True), None


  def update_user(self,context, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.update_user(context, args)
    if err:
      return None, err
    return serialize(user), None

  def delete_user(self, context: Context, user_id) -> (dict, MassEnergizeAPIError):
    user, err = self.store.delete_user(context, user_id)
    if err:
      return None, err
    return serialize(user), None


  def list_users_for_community_admin(self, context, community_id) -> (list, MassEnergizeAPIError):
    users, err = self.store.list_users_for_community_admin(context, community_id)
    if err:
      return None, err
    return serialize_all(users), None


  def list_users_for_super_admin(self, context) -> (list, MassEnergizeAPIError):
    users, err = self.store.list_users_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(users), None


  def add_action_todo(self, context, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.add_action_todo(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None

  def add_action_completed(self, context, args) -> (dict, MassEnergizeAPIError):
    user, err = self.store.add_action_completed(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None
  
  def handle_csv(self, context, args) -> (dict, MassEnergizeAPIError):

    first_name_field = args.get('first_name_field', None)
    last_name_field = args.get('last_name_field', None)
    email_field = args.get('email_field', None)

    custom_message = args.get('message', "")

    csv_ref = args.get('csv', None)
    if csv_ref:
      csv_ref = csv_ref.file
    else:
      return None, CustomMassenergizeError("csv file not specified")

    filecontents, err = _parse_import_file(csv_ref)
    if err:
      return None, CustomMassenergizeError(err)

    invalid_emails = []
    line = 0
    for csv_row in filecontents:
      column_list = list(csv_row.keys())
      ###values_list= list(csv_row.values())
      try:
        # prevents the first row (headers) from being read in as a user
        #print(csv_row[first_name_field])
        if csv_row[first_name_field] == column_list[0]:
          continue
        # verify correctness of email address
        line += 1
        first_name = csv_row[first_name_field]
        last_name = csv_row[last_name_field]
        email = csv_row[email_field]
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if(re.search(regex,email)):   
          info, err = self.store.import_from_csv(context, args, first_name, last_name, email)

          # send invitation e-mail to each new user
          _send_invitation_email(info, custom_message)

        else:
          if filecontents.index(csv_row) != 0:
            invalid_emails.append({"line":line, "email":email}) 

      except Exception as e:
        print(str(e))
        return None, CustomMassenergizeError(str(e))
    if err:
      return None, err
    return {'invalidEmails': invalid_emails}, None