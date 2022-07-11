from __future__ import print_function

from requests import request
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
from django.forms.models import model_to_dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path
import re
CLEANER = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
SCOPES = ["https://www.googleapis.com/auth/documents.readonly", 'https://www.googleapis.com/auth/drive']

from api.store.utils import get_community

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()

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

  def export_action(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    # gets action info
    action, err = self.store.get_action_info(context, args)
    if err:
        return None, err

    action_dict = model_to_dict( action )

    # creates and populates google doc with action info
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
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)

        # creating new google doc
        title = action_dict['title']
        body = {
            'title': title
        }
        doc = service.documents() \
            .create(body=body).execute()

        requests = []
        index_prev = 0
        skip_fields = ["id", "icon", "image", "user", "properties", "geographic_area", "average_carbon_score", "primary_category"] 

        FIELD_NAMES = {
            "title"             : "TITLE",
            "rank"              : "RANK",
            "featured_summary"  : "FEATURED SUMMARY",
            "steps_to_take"     : "FEATURED SUMMARY",
            "deep_dive"         : "DEEP DIVE",
            "about"             : "ABOUT",
            "calculator_action" : "CALCULATOR ACTION",
            "community"         : "COMMUNITY",
            "is_deleted"        : "IS DELETED",
            "is_published"      : "IS PUBLISHED",
            "tags"              : "TAGS",
            "vendors"           : "VENDORS",
            "is_global"         : "IS TEMPLATE"
            
        }

        for k in list(action_dict):
            if k not in skip_fields:
                key = FIELD_NAMES[k]
                value = action_dict[k]

                if key == "COMMUNITY":
                    community, err = get_community(community_id=value)
                    if err:
                        return None, err
                    value = community.name

                if key == "CALCULATOR ACTION":
                    # TODO: replace CCAction number with name
                    pass

                if key == "VENDORS":
                    vendors = []
                    for v in value:
                        vendors.append(v.name)
                    value = ", ".join(vendors)

                if key == "TAGS":
                    location_tags = []
                    cost_tag = ""
                    impact_tag = ""
                    category_tag = ""
                    for t in value:
                        tag = t.name
                        if t.tag_collection.name == "Own/Rent/Condo":
                            location_tags.append(tag)
                        elif t.tag_collection.name == "Cost":
                            cost_tag = tag
                        elif t.tag_collection.name == "Impact":
                            impact_tag = tag
                        else:
                            category_tag = tag

                    value = "Category: {}\nCost: {}\nImpact: {}\nOwn/Rent/Condo: {}".format(category_tag, cost_tag, impact_tag, ", ".join(location_tags))  
  
                if isinstance(value, str):
                    # filters out HTML tags
                    # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
                    value = re.sub(CLEANER, '', value)
                
                if value == None or value == [] or value == "":
                    value = "N/A"
                
                value = str(value)
                while value[-1] == '\n':
                    value = value[:-1]

                text = "{}\n{}\n\n".format(key, value)

                requests += [
                    {
                       'insertText': {
                        'location': {
                            'index': 1 + index_prev
                        },
                        'text' : text
                    }},
                    {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': 1 + index_prev,
                            'endIndex': 1 + index_prev + len(key)
                        },
                        'textStyle': {
                            'underline': True
                        },
                        'fields': 'underline'
                    }}
                ]

                index_prev += len(text)

        result = service.documents().batchUpdate(documentId=doc.get("documentId"), body={'requests': requests}).execute()
    except HttpError as e:
        print(e)
        return None, e

    return {"success": True}, None

