from __future__ import print_function
from urllib import request

from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from api.store.action import ActionStore
from _main_.utils.context import Context
from _main_.utils.constants import ADMIN_URL_ROOT
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from .utils import send_slack_message
from api.store.utils import get_user_or_die, get_community
from sentry_sdk import capture_message
from typing import Tuple
from django.forms.models import model_to_dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from html.parser import HTMLParser
from html.entities import name2codepoint

import os.path
import re
CLEANER = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/drive']

from carbon_calculator.models import Action as CCAction
from api.store.media_library import MediaLibraryStore
from api.store.utils import get_user
from datetime import datetime

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()
    self.media_store = MediaLibraryStore()

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
            CURR_DIR = os.path.dirname(os.path.realpath(__file__))
            flow = InstalledAppFlow.from_client_secrets_file(
                CURR_DIR+'/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)
        drive = build('drive', 'v3', credentials=creds)
        title = action_dict['title']

        # folder where new folder and doc will be placed, specified by user
        PARENT_FOLDER_ID = args.get('folder', None) if not None else "root"
        
        # creating new folder
        folder_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [PARENT_FOLDER_ID]
        }
        folder = drive.files().create(body=folder_metadata, fields='id').execute()
        FOLDER_ID = folder['id']

        # creating new google doc by making a copy of the export template google doc
        body = {
            'name': title,
            'parents': [FOLDER_ID] # parent is 'root' if folder is 'MyDrive'
        }
        TEMPLATE_ID = "1dmhMOZQp6mnk1_8xbCxHZnpChlhji0av_supMe147gU"
        doc = drive.files().copy(fileId=TEMPLATE_ID, body=body, supportsAllDrives=True, supportsTeamDrives=True).execute()
        DOCUMENT_ID = doc['id']
        
        # TODO: create a file instead of copying template??
        # doc = drive.files().create(body=body, supportsAllDrives=True, supportsTeamDrives=True, fields='id').execute()

        skip_fields = ["id", "properties", "geographic_area", "average_carbon_score", "primary_category", "is_deleted", "is_published", "is_global", "rank", "icon", "user"] 
        html_fields = ["ABOUT", "STEPS TO TAKE", "DEEP DIVE"]
        
        class MyHTMLParser(HTMLParser):
            pass
        parser = MyHTMLParser()

        # order of fields will dictate the order of fields in Doc
        FIELD_NAMES = {
            "title"             : "TITLE", # no check needed
            "community"         : "COMMUNITY", # check neded
            "tags"              : "TAGS", # check neded
            "calculator_action" : "CALCULATOR ACTION", # check neded
            "featured_summary"  : "FEATURED SUMMARY", # no check needed
            "about"             : "ABOUT", # html field
            "steps_to_take"     : "STEPS TO TAKE", # html field
            "deep_dive"         : "DEEP DIVE", # html field
            "vendors"           : "VENDORS", # check neded
            "image"             : "IMAGE", # check neded
        }

        provider = None
        requests = []
        TEMPLATE_END_INDEX = service.documents().get(documentId=TEMPLATE_ID).execute().get("body", {}).get("content", {})[-1].get("endIndex", 1) - 1

        # makes the Doc request object for all headings and non-html action fields
        def get_request(heading_text, value_text, end=None, is_bold=False, is_underline=False):   
            end = end if end else len(value_text)

            # in the case of doc heading (provider and date)
            if not heading_text:
                return [
                    {
                        'insertText': {
                            'location': {
                                'index': TEMPLATE_END_INDEX,
                            },
                            'text': value_text
                        }   
                    },
                    {
                        'updateTextStyle': {
                            'range': {
                                'startIndex': TEMPLATE_END_INDEX,
                                'endIndex': TEMPLATE_END_INDEX + end
                            },
                            'textStyle': {
                                'bold': is_bold,
                                'underline': is_underline
                            },
                            'fields': 'bold, underline'
                        }
                    },
                    {
                        'updateTextStyle': {
                            'range': {
                                'startIndex': TEMPLATE_END_INDEX + end,
                                'endIndex': TEMPLATE_END_INDEX + len(value_text)
                            },
                            'textStyle': {},
                            'fields': 'bold, underline'
                        }
                    },
                ]
            
            # in the case of action fields
            return [
                {
                    'insertText': {
                        'location': {
                            'index': TEMPLATE_END_INDEX,
                        },
                        'text': value_text
                    }   
                },
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': TEMPLATE_END_INDEX,
                            'endIndex': TEMPLATE_END_INDEX + len(value_text)
                        },
                        'textStyle': {},
                        'fields': '*'
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': TEMPLATE_END_INDEX,
                        },
                        'text': heading_text
                    }   
                }, 
                {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': TEMPLATE_END_INDEX,
                            'endIndex': TEMPLATE_END_INDEX + len(heading_text)
                        },
                        'textStyle': {
                            'bold': True,
                            'underline': True
                        },
                        'fields': 'bold, underline'
                    }
                },
            ]

        # reversing order of field names to preserve correct order (much easer to add to Doc backwards)
        for f in list(FIELD_NAMES)[::-1]:
            # print("On field:", f)
            field = FIELD_NAMES[f]
            value = action_dict[f]

            if not value:
                requests += get_request(field + '\n', "N/A\n\n")
            else:
                if field in html_fields:
                    #TODO: handle html fields
                    pass
                elif field == "COMMUNITY":
                    community, err = get_community(community_id=value)
                    if err:
                        return None, err
                    
                    value = community.name
                    requests += get_request(field + '\n', value + '\n\n')

                elif field == "CALCULATOR ACTION":
                    # TODO: error handling if .get() doesn't return anything
                    cc_action = CCAction.objects.get(id=value)
                    
                    value = cc_action.description
                    requests += get_request(field + '\n', value + '\n\n')

                elif field == "VENDORS":
                    vendors = []
                    for v in value:
                        vendors.append(v.name)
                    
                    value = ", ".join(vendors)
                    requests += get_request(field + '\n', value + '\n\n')

                elif field == "TAGS":
                    location_tags = []
                    cost_tag = None
                    impact_tag = None
                    category_tag = None
                    tags = ""
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

                    # TODO: check formatting when there are no tags, and when there are no location tags
                    if category_tag:
                        tags += "{} / ".format(category_tag)
                    if cost_tag:
                        tags += "{} / ".format(cost_tag)
                    if impact_tag:
                        tags += "{} / ".format(impact_tag)
                    if len(location_tags) != 0:
                        tags += ", ".join(location_tags)
                    
                    value = tags
                    requests += get_request(field + '\n', value + '\n\n')

                elif field == "IMAGE":
                    img, err = self.media_store.getImageInfo({'media_id': value})
                    if err:
                        return None, err
                    
                    value = img.simple_json()['url']
                    requests += get_request(field + '\n', value + '\n\n')

                else:
                    # title and featured summary
                    requests += get_request(field + '\n', value + '\n\n')

        # adding provider, user, and date information
        requests += get_request(None, "WHEN:\t\t\t{}\n\n".format(datetime.now().strftime("%d %B, %Y")), is_bold=True, end=len("WHEN:"))

        provider = None    
        if action_dict['user']:
            provider, err = get_user(action_dict['user'])
            if err:
                return None, err

        if provider and provider != args['exporter_name']:
            provider_text = "\nWHO PROVIDIED THIS?\t{}, {}\n".format(provider, args['exporter_name'])
        else:
            provider_text = "\nWHO PROVIDED THIS?\t{}\n".format(args['exporter_name'])
        
        requests += get_request(None, provider_text, is_bold=True, end=len("WHO PROVIDED THIS?"))
        
        ### BELOW IS ONLY NEEDED IF NEW DOC IS CREATED INSTEAD OF COPIED FROM TEMPLATE ###

        # adding header (massEnergize logo, export action template, instructions link)
        # heading = "\nExport Action Template\n\n"
        # instructions_link = "https://docs.google.com/document/d/1GBt7-7keBwnusnstdEQA83WK3g1tId7K9rMUmPK0vXc/edit"
        # instructions_text = "Instructions for submitting or modifying actions here\n"

        # requests += [
        #     {
        #         'insertText': {
        #             'location': {
        #                 'index': 1,
        #             },
        #             'text': instructions_text
        #         }   
        #     },
        #     {
        #         'updateTextStyle': {
        #             'range': {
        #                 'startIndex': 1,
        #                 'endIndex': len(instructions_text)
        #             },
        #             'textStyle': {
        #                 'bold': True,
        #                 'underline': True,
        #                 'link': {
        #                     'url': instructions_link
        #                 }
        #             },
        #             'fields': 'bold, underline'
        #         }
        #     },
        #     {
        #         'insertText': {
        #             'location': {
        #                 'index': 1,
        #             },
        #             'text': heading
        #         }   
        #     },
        #     {
        #         'updateTextStyle': {
        #             'range': {
        #                 'startIndex': 1,
        #                 'endIndex': len(heading)
        #             },
        #             'textStyle': {
        #                 'bold': True,
        #                 'fontSize': {
        #                     'magnitude': 15,
        #                     'unit': 'PT'
        #                 },
        #             },
        #             'fields': 'bold'
        #         }
        #     },
        #     {
        #         'insertInlineImage': {
        #             'location': {
        #                 'index': 1
        #             },
        #             'uri':
        #                 'https://fonts.gstatic.com/s/i/productlogos/docs_2020q4/v6/web-64dp/logo_docs_2020q4_color_1x_web_64dp.png',
        #             'objectSize': {
        #                 'height': {
        #                     'magnitude': 50,
        #                     'unit': 'PT'
        #                 },
        #                 'width': {
        #                     'magnitude': 50,
        #                     'unit': 'PT'
        #                 }
        #             }
        #         }
        #     }
        # ]

        # populates doc with all content and styling
        service.documents().batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()
    except HttpError as e:
        print(e)
        return None, e

    return {"success": True}, None