from __future__ import print_function
from dataclasses import field
from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from api.store.action import ActionStore
from _main_.utils.context import Context
from _main_.utils.constants import ADMIN_URL_ROOT
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from .utils import send_slack_message
from api.store.utils import get_user_or_die
from sentry_sdk import capture_message
from typing import Tuple

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from api.store.vendor import VendorStore
from api.store.community import CommunityStore
from api.store.tag import TagStore
from api.store.utils import get_community
from carbon_calculator.carbonCalculator import CarbonCalculator

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()
    self.vendor_store = VendorStore()
    self.community_store = CommunityStore()
    self.tag_store = TagStore()
    self.carbon_calc = CarbonCalculator()

  def import_action(self, docID) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        # If modifying these scopes, delete the file token.json.
        SCOPES = ["https://www.googleapis.com/auth/documents.readonly", 'https://www.googleapis.com/auth/drive']
        # second is needed to edit OTHERS' files, /auth/drive,file needed to only edit OUR OWN files

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                CURR_DIR = os.path.dirname(os.path.realpath(__file__))
                flow = InstalledAppFlow.from_client_secrets_file(
                    CURR_DIR+'/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

   
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=docID).execute()

        # gets all of the content in the google doc
        doc = document.get("body").get("content")
        
        # excludes lines for metadata, title, instructions in doc
        buffer = 13

        # mapping from doc field names to frontend form field names
        FIELD_NAMES = {
            "CATEGORY TAG"      : "Category",
            "COST TAG"          : "Cost",
            "IMPACT TAG"        : "Impact",
            "OWN/RENT/CONDO TAG": "Own/Rent/Condo",
            "TITLE"             : "title",
            "RANK"              : "rank",
            "ABOUT"             : "about",
            "IS TEMPLATE"       : "is_global",
            "COMMUNITY"         : "community",
            "CALCULATOR ACTION" : "calculator_action",
            "FEATURED SUMMARY"  : "featured_summary",
            "STEPS TO TAKE"     : "steps_to_take",
            "DEEP DIVE"         : "deep_dive",
            "VENDORS"           : "vendors"
        }

        # mapping from community name to community subdomain
        SUBDOMAINS = {}
        all_communities, err = self.community_store.list_communities({'is_sandbox': False}, {})
        if err:
            return None, err
        for c in all_communities:
            info = c.info()
            SUBDOMAINS[info['name']] = info['subdomain']
        
        fields = {}
        for i in range(buffer, len(doc), 2):
            field = FIELD_NAMES[doc[i].get("paragraph").get("elements")[0].get("textRun").get("content")[:-2]]
            data = doc[i+1].get("paragraph").get("elements")[0].get("textRun").get("content")
            data = data[:-1] if data[-1] == '\n' else data

            if field == "vendors" or field == "Category" or field == "Cost" or field == "Impact" or field == "Own/Rent/Condo":
                multi = data.split(',')
                data = []
                for x in multi:
                    data.append(x.strip())

            if field == "community":
                fields['subdomain'] = SUBDOMAINS[data]

            if field == "is_global":
                if data.lower() == "no" or data.lower() == "false":
                    data = "false"
                else:
                    data = "true"
            
            fields[field] = data
        
        # check that supplied community exists
        if not fields.get('subdomain', None):
            fields['community'] = ""
            fields['vendors'] = []
        else:
            community, err = get_community(subdomain=fields['subdomain'])
            if err:
                return None, err
            community_id = community.info()['id']

            # check that vendor[s] are valid for supplied community        
            vendors_qs, err = self.vendor_store.list_vendors({'is_sandbox': False}, {"community_id": community_id})
            if err:
                return None, err
            vendors = vendors_qs.values_list('name', flat=True)

            for v in fields['vendors']:
                if v not in vendors:
                    fields['vendors'].remove(v)

            # check that category is valid
            # TODO: should be using community specific tags but line below is not working
            # tags, err = self.tag_store.list_tags(community_id)
            tags, err = self.tag_store.list_tags_for_super_admin()
            if err:
                return None, err

        #     print("here")
        #     # print([[tag.name] for tag in tags if tag.tag_collection == "Cost"])
        #     # if fields['Category'] not in [[tag.name] for tag in tags if tag.tag_collection == "Category"]:
        #     #     print("here - ca")
        #     #     fields['Category'] = []
        #     all_categories = []
        #     all_costs = []
        #     all_impacts = []
        #     all_own_rent_condo = []
        #     for t in tags:
        #         tag = t.name
        #         if t.tag_collection.name == "Category":
        #             all_categories.append(tag)
        #         elif t.tag_collection.name == "Cost":
        #             all_costs.append(tag)
        #         elif t.tag_collection.name == "Impact":
        #             all_impacts.append(tag)
        #         else:
        #             all_own_rent_condo.append(tag)
        #     print(all_costs)

        #     print("here2")

        # tags, err = self.tag_store.list_tags_for_super_admin()
        # if err:
        #     return None, err

        # # check that only one cost and impact are provided and they are valid
        # if fields['Cost'] not in [[tag.name] for tag in tags if tag.tag_collection.name == "Cost"]:
        #     print("here - co")
        #     fields['Cost'] = []
        # if fields['Impact'] not in [[tag.name] for tag in tags if tag.tag_collection.name == "Impact"]:
        #     print("here - i")
        #     fields['Impact'] = []

        # # check that location value[s] are valid
        # locations = [tag.name for tag in tags if tag.tag_collection.name == "Own/Rent/Condo"]
        # for l in fields['Own/Rent/Condo']:
        #     if l not in locations:
        #         fields['Own/Rent/Condo'].remove(l)

        # TODO: Validate carbon calculator input
        if not field['calculator_action'] or not len(self.carbon_calc.Query(action=field['calculator_action']) == 1):
            field['calculator_action'] = ""

        
        print("SENDING:", fields)
        return fields, None
    
    except Exception as e:
        return None, e
  
  def get_action_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.get_action_info(context, args)
    if err:
      return None, err
    return serialize(action, full=True), None

  def list_actions(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    actions, err = self.store.list_actions(context, args)
    if err:
      return None, err
    return serialize_all(actions), None


  def create_action(self, context: Context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      action, err = self.store.create_action(context, args)
      if err:
        return None, err

      if user_submitted:

        # For now, send e-mail to primary community contact for a site
        admin_email = action.community.owner_email
        admin_name = action.community.owner_name
        first_name = admin_name.split(" ")[0]
        if not first_name or first_name == "":
          first_name = admin_name

        community_name = action.community.name

        user = get_user_or_die(context, args)
        if user:
          name = user.full_name
          email = user.email
        else:
          return None, CustomMassenergizeError('Action submission incomplete')

        subject = 'User Action Submitted'

        content_variables = {
          'name': first_name,
          'community_name': community_name,
          'url': f"{ADMIN_URL_ROOT}/admin/edit/{action.id}/action",
          'from_name': name,
          'email': email,
          'title': action.title,
          'body': action.featured_summary,
        }
        send_massenergize_rich_email(
              subject, admin_email, 'action_submitted_email.html', content_variables)

        send_slack_message(
            #SLACK_COMMUNITY_ADMINS_WEBHOOK_URL, {
            SLACK_SUPER_ADMINS_WEBHOOK_URL, {
            "content": "User submitted Action for "+community_name,
            "from_name": name,
            "email": email,
            "subject": action.title,
            "message": action.featured_summary,
            "url": f"{ADMIN_URL_ROOT}/admin/edit/{action.id}/action",
            "community": community_name
        }) 

      return serialize(action), None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_action(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.update_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def rank_action(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.rank_action(args)
    if err:
      return None, err
    return serialize(action), None

  def delete_action(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.delete_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def copy_action(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    action, err = self.store.copy_action(context, args)
    if err:
      return None, err
    return serialize(action), None

  def list_actions_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    actions, err = self.store.list_actions_for_community_admin(context, args)
    if err:
      return None, err
    return serialize_all(actions), None


  def list_actions_for_super_admin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    actions, err = self.store.list_actions_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(actions), None
