from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from api.store.userprofile import UserStore
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from _main_.utils.constants import COMMUNITY_URL_ROOT,  ME_LOGO_PNG
import os, csv
import re
from _main_.utils.massenergize_logger import log
from typing import Tuple
from api.utils.api_utils import get_sender_email

from api.utils.filter_functions import sort_items



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

  # send email inviting user to complete their profile
  cadmin_name = user_info.get("cadmin", "The Community Administrator")
  cadmin_email = user_info.get("cadmin_email", "no-reply@massenergize.org")
  cadmin_firstname = cadmin_name.split(" ")[0]
  community_name = user_info.get("community", None)
  community_logo = user_info.get("community_logo", None)
  community_info = user_info.get("community_info", None)
  location = user_info.get("location", None)
  subdomain = user_info.get("subdomain", "global")
  email = user_info.get("email", None)
  first_name = user_info.get("first_name", None)
  team_name = user_info.get("team_name", None)
  team_leader = user_info.get('team_leader', None)
  team_leader_firstname = user_info.get('team_leader_firstname', None)
  team_leader_email = user_info.get('team_leader_email', None)
  team_id = user_info.get('team_id', 0)

  if team_name == 'none' or team_name == "None":
    team_name = None
  if team_name:
    email_template = 'team_invitation_email.html'
  else:
    email_template = 'community_invitation_email.html'

  if mess and mess != "":
    if team_name:
      custom_intro = "Here is a welcome message from " + team_leader_firstname
    else:
      custom_intro = "Here is a welcome message from " + cadmin_firstname
    custom_message = mess
  else:
    custom_intro = "Here is how " + cadmin_firstname + " describes " + community_name
    custom_message = community_info

  subject = cadmin_name + " invites you to join the " + community_name + " Community"

  #community_logo =  community.logo.file.url if community and community.logo else ME_LOGO_PNG
  #subdomain =   community.subdomain if community else "global"
  #subject = f'Welcome to {community_name}, a MassEnergize community'
  homelink = f'{COMMUNITY_URL_ROOT}/{subdomain}'
  
  content_variables = {
    'name': first_name,
    'community': community_name,
    'community_admin': cadmin_name,
    'community_admin_firstname': cadmin_firstname,
    'homelink': homelink,
    'logo': community_logo,
    'location': location,
    'team': team_name,
    'team_leader': team_leader,
    'team_leader_firstname': team_leader_firstname,
    'team_leader_email': team_leader_email,
    'custom_intro': custom_intro,
    'custom_message': custom_message,
    'contactlink':f'{homelink}/contactus',
    'teamlink': f'{homelink}/teams/{team_id}',
    'signuplink': f'{homelink}/signin',
    'privacylink': f"{homelink}/policies?name=Privacy%20Policy"
    }
  
  #send_massenergize_rich_email(subject, email, email_template, content_variables, cadmin_email)
  send_massenergize_rich_email(subject, email, email_template, content_variables)

class UserService:
  """
  Service Layer for all the users
  """

  def __init__(self):
    self.store =  UserStore()

  def fetch_user_visits(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    visits, err = self.store.fetch_user_visits(context, args)
    if err:
      return None, err
    return list(visits), None
    # If we are using logs instead of footages, uncomment this
    # return visits, None

    
  def accept_mou(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    user, err = self.store.accept_mou(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None
  
  def get_user_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    user, err = self.store.get_user_info(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None

  def add_household(self,context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    household, err = self.store.add_household(context, args)
    if err:
      return None, err
    return serialize(household, full=True), None

  def edit_household(self,context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    household, err = self.store.edit_household(context, args)
    if err:
      return None, err
    return serialize(household, full=True), None

  def remove_household(self,context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    household, err = self.store.remove_household(context, args)
    if err:
      return None, err
    return household, None

  def list_users(self,context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    user, err = self.store.list_users(context,community_id)
    if err:
      return None, err
    return user, None


  def list_publicview(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    publicview, err = self.store.list_publicview(context, args)
    if err:
      return None, err
    return {'public_user_list': publicview}, None

  def list_actions_todo(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    actions_todo, err = self.store.list_todo_actions(context, args)
    if err:
      return None, err
    return serialize_all(actions_todo), None

  def list_actions_completed(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    actions_completed, err = self.store.list_completed_actions(context, args)
    if err:
      return None, err
    return  serialize_all(actions_completed), None

  def remove_user_action(self, context: Context, user_action_id) -> Tuple[list, MassEnergizeAPIError]:
    result, err = self.store.remove_user_action(context, user_action_id)
    if err:
      return None, err
    return result, None

  def list_events_for_user(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    events, err = self.store.list_events_for_user(context, args)
    if err:
      return None, err
    return serialize_all(events), None

  def check_user_imported(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    imported_info, err = self.store.check_user_imported(context, args)
    if err:
      return None, err
    return imported_info, None
  
  def complete_imported_user(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    imported_info, err = self.store.complete_imported_user(context, args)
    if err:
      return None, err
    return imported_info, None

  def validate_username(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    info, err = self.store.validate_username(args)
    if err:
      return None, err
    return info, None

  def create_user(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      res, err = self.store.create_user(context, args)
      if err:
        return None, err

      community = res["community"]
      user = res["user"]
      send_email = res["new_user_email"]
      if send_email:   # a complete user profile, not a guest
        community_name =  community.name if community else "Global Massenergize Community"
        community_logo =  community.logo.file.url if community and community.logo else ME_LOGO_PNG
        subdomain =   community.subdomain if community else "global"
        subject = f'Welcome to {community_name}, a MassEnergize community'
        homelink = f'{COMMUNITY_URL_ROOT}/{subdomain}'

        from_email = get_sender_email(community.id)

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

        send_massenergize_rich_email(subject, user.email, 'user_registration_email.html', content_variables, from_email)
      user = serialize(user, full=True)
      return {**user, "is_new":True }, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def update_user(self,context, args) -> Tuple[dict, MassEnergizeAPIError]:
    user, err = self.store.update_user(context, args)
    if err:
      return None, err
    return serialize(user), None

  def delete_user(self, context: Context, user_id) -> Tuple[dict, MassEnergizeAPIError]:
    user, err = self.store.delete_user(context, user_id)
    if err:
      return None, err
    return serialize(user), None


  def list_users_for_community_admin(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    users, err = self.store.list_users_for_community_admin(context, args)
    if err:
      return None, err
    sorted = sort_items(users, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_users_for_super_admin(self, context,args) -> Tuple[list, MassEnergizeAPIError]:
    users, err = self.store.list_users_for_super_admin(context,args)
    if err:
      return None, err
    sorted = sort_items(users, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def add_action_todo(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    user, err = self.store.add_action_todo(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None

  def add_action_completed(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    user, err = self.store.add_action_completed(context, args)
    if err:
      return None, err
    return serialize(user, full=True), None
  
  def import_from_csv(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
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
        line += 1
        column_list = list(csv_row.keys())
        try:
          # prevents the first row (headers) from being read in as a user
          first_name = csv_row[first_name_field].strip()
          last_name = csv_row[last_name_field]
          email = csv_row[email_field].lower()

          if first_name == column_list[0]:
            continue

          # verify correctness of email address
          # improved regex for validating e-mails
          regex = '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
          if(re.search(regex,email)):  
            info, err = self.store.add_invited_user(context, args, first_name, last_name, email)

            # send invitation e-mail to each new user
            _send_invitation_email(info, custom_message)

          else:
            if filecontents.index(csv_row) != 0:
              invalid_emails.append({"line":line, "email":email}) 

        except Exception as e:
          print("Error string: " + str(e))
          return None, CustomMassenergizeError(e)
      if err:
        return None, err
      return {'invalidEmails': invalid_emails}, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def import_from_list(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      names = args.get('names', None)
      first_names = args.get('first_names', None)
      last_names = args.get('last_names', None)
      emails = args.get('emails', None)      

      custom_message = args.get('message', "")

      invalid_emails = []
      for ix in range(len(emails)):
        try:
          if first_names:
            first_name = first_names[ix]
            last_name = last_names[ix]
          else:
            name = names[ix]
            spc = name.find(' ')
            first_name = name[0:spc-1]
            last_name = name[spc+1]
          email = emails[ix].lower()

          # improved regex for validating e-mails
          regex = '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
          if(re.search(regex,email)):  
            info, err = self.store.add_invited_user(context, args, first_name, last_name, email)
            if err:
              return None, err

            # send invitation e-mail to each new user
            _send_invitation_email(info, custom_message)

          else:
            invalid_emails.append({"line":ix, "first_name":first_name, "last_name": last_name, "email":email}) 

        except Exception as e:
          print(str(e))
          return None, CustomMassenergizeError(e)
      return {'invalidEmails': invalid_emails}, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
    


  def update_loosed_user(self, context, args):
    res, err = self.store.update_loosed_user(context, args)
    if err:
      return None, err
    
    return serialize(res, full=True), None
  

  def get_loosed_user(self, context, args):
    res, err = self.store.get_loosed_user(context, args)
    if err:
      return None, err
    
    return res.info(), None
