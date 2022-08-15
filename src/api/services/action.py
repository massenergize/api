from __future__ import print_function
from cgitb import html
from dataclasses import dataclass
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
from api.store.media_library import MediaLibraryStore
from api.store.utils import get_community
from carbon_calculator.carbonCalculator import CarbonCalculator
from django.core.exceptions import ObjectDoesNotExist
import re

class ActionService:
  """
  Service Layer for all the actions
  """

  def __init__(self):
    self.store =  ActionStore()
    
    # below is used only for importing actions
    self.vendor_store = VendorStore()
    self.community_store = CommunityStore()
    self.tag_store = TagStore()
    self.media_store = MediaLibraryStore()
    self.carbon_calc = CarbonCalculator()

  def import_action(self, docID, communities) -> Tuple[dict, MassEnergizeAPIError]:
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
            "TITLE"             : "title",
            "RANK"              : "rank",
            "IS TEMPLATE"       : "is_global",
            "COMMUNITY"         : "community",
            "CATEGORY TAG"      : "Category",
            "COST TAG"          : "Cost",
            "IMPACT TAG"        : "Impact",
            "OWN/RENT/CONDO TAG": "Own/Rent/Condo",
            "CALCULATOR ACTION" : "calculator_action",
            "FEATURED SUMMARY"  : "featured_summary",
            "ABOUT"             : "about",
            "STEPS TO TAKE"     : "steps_to_take",
            "DEEP DIVE"         : "deep_dive",
            "VENDORS"           : "vendors",
            "IMAGE LINK"        : "image",
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
        doc_idx = buffer + 1 # skipping title of 'title' field
        field_names_keys = list(FIELD_NAMES)
        arr_fields = ["vendors", "Category", "Cost", "Impact", "Own/Rent/Condo"]
        html_fields = ["about", "steps_to_take", "deep_dive"]
        
        def process_html_data(data):
            # need to parse out:
            # - text DONE
            # - bullets DONE
            # - links DONE
            # - font DONE
            # - font size DONE
            # - font color DONE
            # - styling (bold, italics, underline) DONE
            # print("all", data)
            # print("paragraph", data[0]['paragraph'])
            # print("elements", data[0]['paragraph']['elements'])
            output = ""
            in_unordered_list = False
            in_ordered_list = False
            list_nest_level = 0
            
            # support for more types of bullets is just a matter of noting more of the Doc IDs
            UNORDERED_LIST = "kix.l2c1kf1n3bo0"
            ORDERED_LIST = ["kix.56eudp6yx4bc", "kix.2x1fecli05g8"]

            for obj in data:
                for elem in obj.get('paragraph').get('elements'):
                    # print("CONTENT ->", elem.get('textRun'))
                    # print("STYLING ->", elem['textRun']['textStyle'])
                    # print("")
                    content = elem.get('textRun').get('content')
                    styles = elem.get('textRun').get('textStyle')
                    style_string = 'style = "'
                    # print(styles)

                    bold = styles.get('bold')
                    style_string += 'font-weight: bold; ' if bold else ""

                    italic = styles.get('italic')
                    style_string += 'font-style: italic; ' if italic else ""

                    underline = styles.get('underline')
                    style_string += 'text-decoration: underline; ' if underline else ""
                    
                    size = styles.get('fontSize').get('magnitude')
                    style_string += 'font-size: ' + str(size) + 'px; ' if size else ""

                    font = styles.get('weightedFontFamily', {}).get('fontFamily')
                    style_string += 'font-family: ' + font + '; ' if font else ""

                    red_color = styles.get('foregroundColor', {}).get('color', {}).get('rgbColor', {}).get('red', 0)
                    blue_color = styles.get('foregroundColor', {}).get('color', {}).get('rgbColor', {}).get('blue', 0)
                    green_color = styles.get('foregroundColor', {}).get('color', {}).get('rgbColor', {}).get('green', 0)
                    hex_color = '#%02x%02x%02x' % (int(red_color * 255), int(green_color * 255), int(blue_color * 255))
                    style_string += 'color: ' + hex_color + ';'

                    link = styles.get('link', {}).get('url')

                    style_string += '"'

                    new_line = '<br>' if content[-1] == '\n' else ''
                    content = content[:-1] if new_line else content

                    html_string = ""

                    if obj.get('paragraph', {}).get('bullet') and content != "":
                        # accounts for extra new line since html bullets have padding
                        output = output[:-4] if output[-4:] == '<br>' else output
                        # makes new ordered list if nested bullet, otherwise just adds ordered list item
                        if in_ordered_list:
                            if obj.get('paragraph', {}).get('bullet', {}).get('nestingLevel'):
                                html_string = '<ol><li {}>{}</li>'.format(style_string, content)
                                list_nest_level += 1
                            else:
                                # closes nested lists (if necessary) and adds list item
                                html_string = ('</ol>' * list_nest_level) + '<li {}>{}</li>'.format(style_string, content)
                                list_nest_level = 0

                        # makes new unordered list if nested bullet, otherwise just adds unordered list item
                        elif in_unordered_list:
                            if obj.get('paragraph', {}).get('bullet', {}).get('nestingLevel'):
                                html_string = '<ul><li {}>{}</li>'.format(style_string, content)
                                list_nest_level += 1
                            else:
                                # closes nested lists (if necessary) and adds list item
                                html_string = ('</ul>' * list_nest_level) + '<li {}>{}</li>'.format(style_string, content)
                                list_nest_level = 0
                        
                        # new list case, creating corresponding list type ((un)ordered) based on 'listId'
                        elif obj.get('paragraph', {}).get('bullet', {}).get('listId') in ORDERED_LIST:
                            html_string = '<ol><li {}>{}</li>'.format(style_string, content)
                            in_ordered_list = True
                        else:
                            # unordered list is 'catch all' case
                            html_string = '<ul><li {}>{}</li>'.format(style_string, content)
                            in_unordered_list = True
                    
                    # not in, or no longer in, a list
                    else:
                        if in_ordered_list:
                            # by default there is at least one list to close, more close tags needed for nested bullets
                            html_string = '</ol>' + '</ol>' * list_nest_level

                            in_ordered_list = False
                            list_nest_level = 0
                        elif in_unordered_list:
                            html_string = '</ul>' + '</ul>' * list_nest_level
                            
                            in_unordered_list = False
                            list_nest_level = 0

                        if content == '':
                            html_string += '{}'.format(new_line)
                        elif link:
                            html_string += '<a {} href="{}">{}</a>{}'.format(style_string, link, content, new_line)
                        else:
                            html_string += '<span {}>{}</span>{}'.format(style_string, content, new_line)
                        
                    output += html_string
            
            if in_ordered_list:
                output += '</ol>'
            elif in_unordered_list:
                output += '</ul>'

            # print('OUTPUT:', output)
            return output

        # print(doc[doc_idx:])
        # return {}, {}
        for i in range(0,len(FIELD_NAMES)):
            field = FIELD_NAMES[field_names_keys[i]]
            data = [] if field in html_fields else ""

            if i == len(FIELD_NAMES) - 1:
                for j in range(doc_idx, len(doc)):
                    data += doc[j].get("paragraph").get("elements")[0].get("textRun").get("content").strip()  
            else:
                while i != len(FIELD_NAMES) - 1 and doc[doc_idx].get("paragraph").get("elements")[0].get("textRun").get("content").strip() != field_names_keys[i+1]:
                    if field in html_fields:
                        data.append(doc[doc_idx])
                    else:
                        data += doc[doc_idx].get("paragraph").get("elements")[0].get("textRun").get("content").strip()

                    doc_idx += 1

                if data and field in arr_fields:
                    multi = data.split(',')
                    data = []
                    for x in multi:
                        data.append(x.strip())

                if field in arr_fields and data == "":
                    data = []

                if field in html_fields:
                    data = process_html_data(data)

                if data and field == "community":
                    fields['subdomain'] = SUBDOMAINS.get(data)

                if field == "is_global":
                    data = "false" if data.lower() == "no" or data.lower() == "false" or not data else "true"

                if data and field == "rank":
                    data = re.sub("[^0-9]", "", data)
                
                doc_idx += 1
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
            fields['community'] = community_id

            # check that vendor[s] are valid for supplied community        
            if len(fields['vendors']) > 0:
                vendors_qs, err = self.vendor_store.list_vendors({'is_sandbox': False}, {"community_id": community_id})
                if err:
                    return None, err

                valid_vendors = []
                for v in fields['vendors']:
                    try:
                        id = vendors_qs.get(name=v).id
                        valid_vendors.append(id)
                    except ObjectDoesNotExist:
                        pass
        
                fields['vendors'] = valid_vendors

            # TODO: crosscheck image link with all public images too
            # check that image link is valid for supplied community
            if len(fields['image']) > 0:
                communities = communities.split(",")
                images, _ = self.media_store.fetch_content({'community_ids':communities})

                found = False
                for img in images:
                    data = img.simple_json()
                    
                    if fields['image'] == data['url']:
                        fields['image'] = [data['id']]
                        found = True
                        break
                
                fields['image'] = fields['image'] if found else []

        # check that tags are valid
        tags, err = self.tag_store.list_tags_for_super_admin()
        if err:
            return None, err
        
        # possibly use tag_collections.list instead
        all_categories = [[tag.name, str(tag.id)] for tag in tags if tag.tag_collection and tag.tag_collection.simple_json()['name'] == "Category"]
        all_costs = [[tag.name, str(tag.id)] for tag in tags if tag.tag_collection and tag.tag_collection.simple_json()['name'] == "Cost"]
        all_impacts = [[tag.name, str(tag.id)] for tag in tags if tag.tag_collection and tag.tag_collection.simple_json()['name'] == "Impact"]
        all_own_rent_condo = [[tag.name, str(tag.id)] for tag in tags if tag.tag_collection and tag.tag_collection.simple_json()['name'] == "Own/Rent/Condo"]

        # check that at most one category, impact, and cost are provided. If more, take only the first
        found = False
        if len(fields['Category']) > 0:
            for name, id in all_categories:
                if fields['Category'][0] == name:
                    fields['Category'][0] = id
                    found = True
                    break

        fields['Category'] = fields['Category'] if found else []

        found = False
        if len(fields['Cost']) > 0:
            for name, id in all_costs:
                if fields['Cost'][0] == name:
                    fields['Cost'][0] = id
                    found = True
                    break

        fields['Cost'] = fields['Cost'] if found else []

        found = False
        if len(fields['Impact']) > 0:
            for name, id in all_impacts:
                if fields['Impact'][0] == name:
                    fields['Impact'][0] = id
                    found = True
                    break

        fields['Impact'] = fields['Impact'] if found else []
    
        # check that all Own/Rent/Condo, if any, are valid
        found = False
        for i in range(len(fields['Own/Rent/Condo'])):
            for name, id in all_own_rent_condo:
                if fields['Own/Rent/Condo'][i] == name:
                    fields['Own/Rent/Condo'][i] = id
                    found = True
                    break

        fields['Own/Rent/Condo'] = fields['Own/Rent/Condo'] if found else []

        # check carbon calculator input
        found = False
        if fields['calculator_action']:
            all_actions = [[str(a['id']), a['description']] for a in self.carbon_calc.AllActionsList()['actions']]
            for id, desc in all_actions:
                if fields['calculator_action'] == desc:
                    fields['calculator_action'] = id
                    found = True

        fields['calculator_action'] = fields['calculator_action'] if found else ""

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
