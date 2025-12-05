import io
import os
import zipfile
import csv
import requests
from PIL import Image
from _main_.utils.common import generate_workbook_with_sheets
from _main_.utils.massenergize_errors import (
    NotAuthorizedError,
    MassEnergizeAPIError,
    InvalidResourceError,
    CustomMassenergizeError,
)
from _main_.utils.context import Context
from collections import Counter
from api.store.utils import get_human_readable_date, get_massachusetts_time
from api.utils.api_utils import is_admin_of_community
from apps__campaigns.models import Campaign, CampaignActivityTracking, CampaignFollow, CampaignLink, CampaignTechnology, CampaignTechnologyFollow, CampaignTechnologyLike, CampaignTechnologyTestimonial, CampaignTechnologyView, CampaignView, Comment
from database.models import (
    UserProfile,
    CommunityMember,
    Action,
    Team,
    UserActionRel,
    Testimonial,
    TeamMember,
    Community,
    Subscriber,
    Event,
    RealEstateUnit,
    Data,
    TagCollection,
    Goal,
    CommunitySnapshot,
    CustomCommunityWebsiteDomain,
    HomePageSettings,
    ImpactPageSettings,
    EventsPageSettings,
    Vendor,
    TestimonialsPageSettings,
    VendorsPageSettings,
    TeamsPageSettings,
    DonatePageSettings,
    AboutUsPageSettings,
    ContactUsPageSettings,
)
from api.store.team import get_team_users
from api.constants import STANDARD_USER, GUEST_USER
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT
from api.store.tag_collection import TagCollectionStore
from django.db.models import Q
from _main_.utils.massenergize_logger import log
from typing import Tuple

from django.utils import timezone
import datetime
from carbon_calculator.carbonCalculator import AverageImpact
from django.db.models import Sum
from uuid import UUID
from carbon_calculator.models import Action as CCAction
from collections import defaultdict


import json
import boto3

import boto3
import requests
import base64
from uuid import uuid4 


EMPTY_DOWNLOAD = (None, None)

def hyperlink(text, link):
    return '=HYPERLINK("'+link+'","'+text+'")'

def update_user(item):
    return item.user.email if item.user and not item.user.is_deleted else ""

def update_date(item):
    return item.updated_at.date() if item.updated_at else ""

class DownloadStore:
    def __init__(self):
        self.name = "Download Store/DB"
        tcs = TagCollectionStore()

        try:
          # for testing with empty database, create tag collection
          tag_collections = TagCollection.objects.filter(name="Category")
          if tag_collections.count() < 1:
              # because of the comma in "Land, Soil & Water" - this probably doesn't work as intended
              tagdata = {
                  "name": "Category",
                  "tags": "Home Energy,Solar,Transportation,Waste & Recycling,Food,Activism & Education,Land, Soil & Water",
              }
              tcs.create_tag_collection(tagdata)

          self.action_categories = TagCollection.objects.get(
              name="Category"
          ).tag_set.all()
        except:
          tag_collections = []
          self.action_categories = []


        self.action_info_columns = [
            "Live", 
            "Action", 
            "Done in last 30 days (count)", 
            "Done (count)",
            "Annual GHG reduced per action (lbs)", 
            "Total annual GHG reduced (lbs)", 
            "To-do (count)", 
            "Testimonials (count)", 
            "Impact",
            "Cost", 
            "Category", 
            "Carbon Calculator Action",
        ]

        self.user_info_columns_1 = [
            "First Name",
            "Last Name",
            "Preferred Name", 
            "Email", 
        ]

        self.user_info_columns_2 = [
            "Zipcode", 
            "Households (count)",
            "Role",
            "Created",
            "Last sign in", 
        ]

        self.user_info_columns_new = [
            "Done (count)",
            "To-do (count)",
            "Testimonials (count)",
            "Teams (count)",
            "Teams",
        ]

        self.team_info_columns = [
            "Team Name", 
            "Members (count)", 
            "Actions done (count)",
            "To-do (count)",
            "Trending action(s)",
            "Testimonials (count)",
            "Total annual GHG reduced (lbs)", 
            "Parent team",
        ]

        self.community_info_columns = [
            "Community",
            "Location",
            "Geographically Focused", 
            "Last Cadmin Login",
            "Primary Community Users (count)",
            "Members (count)",
            "Guests (count)", 
            "Teams (count)",
            "Testimonials (count)",
            "Actions (count)",
            "Events (count)",
            "Actions: User Reported", 
            "Actions: Manual Addition", 
            "Actions: State/Partner Reported",
            "Actions: Total",
            "Actions: Goal",
            "Actions: Goal Fraction",
            "Households: User Reported",
            "Households: Manual Addition",
            "Households: State/Partner Reported",
            "Households: Total",
            "Households: Goal",
            "Households: Goal Fraction",
            "Carbon: User Reported",
            "Carbon: Manual addition",
            "Carbon: State/Partner Reported",
            "Carbon: Total",
            "Carbon: Goal",
            "Carbon: Goal Fraction",
            "Actions per Member",
        ]

        self.metrics_columns = [
            "Is Live",
            "Households Total",
            "Households User Reported",
            "Households Manual Addition",
            "Households Partner",
            "Primary Community Users",
            "Member Count",
            "Actions Live Count",
            "Actions Total" ,
            "Actions Partner",
            "Actions User Reported",
            "Carbon Total",
            "Carbon User Reported" ,
            "Carbon Manual Addition",
            "Carbon Partner",
            "Guest Count",
            "Actions Manual Addition",
            "Events Hosted Current",
            "Events Hosted Past",
            "My Events Shared Current",
            "My Events Shared Past",
            "Events Borrowed From Others Current",
            "Events Borrowed From Others Past",
            "Teams Count",
            "Subteams Count",
            "Testimonials Count",
            "Service Providers Count",
        ]

        self.pagemap_columns = [
            "Page Name",
            "Status",
            "Admin Page Name",
            "Updated on",
            "Updated by",
        ]
        # Fields should include for Actions, Households, Carbon Reduction: user reported, manual addition, goal for this period, (calculated) % of goal.

        # For Actions entered data - the numbers entered into each category.

        self.community_id = None

    def _clean_datetime_for_json(self, obj):
        """
        Recursively clean datetime objects in data structures for JSON serialization
        """
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._clean_datetime_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_datetime_for_json(item) for item in obj]
        else:
            return obj


    def _get_cells_from_dict(self, columns, data):
        cells = ["" for _ in range(len(columns))]

        for key, value in data.items():
            if type(value) == int or type(value) == float:
                value = str(value)
            if not value:
                continue

            cells[columns.index(key)] = value
        return cells

    def _get_compressed_image_url(self, image_url, max_size_kb=200):
        max_width = 1280

        bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
        if not bucket_name:
            return image_url

        s3_client = boto3.client("s3")
        region = s3_client.meta.region_name

        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            original_size_kb = len(response.content) / 1024
            print("IMAGE:", image_url, "SIZE:", round(original_size_kb, 2), "KB")

            if original_size_kb <= max_size_kb:
                return image_url

            image = Image.open(io.BytesIO(response.content))

            if image.mode != "RGB":
                image = image.convert("RGB")

            width, height = image.size

            if width > max_width:
                new_height = int(height * (max_width / width))
                image.thumbnail((max_width, new_height))

            output = io.BytesIO()

            quality = 85
            subsampling = 2
            progressive = True

            while quality > 20:
                output.seek(0)
                output.truncate()

                image.save(
                    output,
                    format="JPEG",
                    quality=quality,
                    optimize=True,
                    subsampling=subsampling,
                    progressive=progressive
                )

                size_kb = len(output.getvalue()) / 1024
                if size_kb <= max_size_kb:
                    break

                quality -= 10

            if len(output.getvalue()) / 1024 > max_size_kb:
                new_width = int(image.width * 0.85)
                new_height = int(image.height * 0.85)
                image = image.resize((new_width, new_height), Image.LANCZOS)

                output.seek(0)
                output.truncate()

                image.save(
                    output,
                    format="JPEG",
                    quality=70,
                    optimize=True,
                    subsampling=subsampling,
                    progressive=progressive
                )

            compressed_data = output.getvalue()
            compressed_kb = len(compressed_data) / 1024
            print("Compressed image size:", round(compressed_kb, 2), "KB")

            object_key = "compressed_images/" + str(uuid4()) + ".jpg"

            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType="image/jpeg",
                ACL="public-read"
            )

            url = "https://" + bucket_name + ".s3." + region + ".amazonaws.com/" + object_key
            return url

        except Exception as e:
            print("Error compressing or uploading:", str(e))
            return ""



    #Given user, returns first part of populated row for Users CSV
    def _get_user_info_cells_1(self, user):
        user_cells_1 = {}

        if isinstance(user, Subscriber):
            full_name = user.name
            if full_name is None:
                first_name = "---"
                last_name = "---"
            else:
                space = full_name.find(" ")
                first_name = full_name[:space]
                last_name = full_name[space + 1 :]
                
            user_cells_1 = {
                "First Name": first_name,
                "Last Name": last_name,
                "Email": user.email,
            }
            return self._get_cells_from_dict(self.user_info_columns_1, user_cells_1)
        elif isinstance(user, RealEstateUnit):
            # for geographic communities, list non-members who have households in the community
            reu = user
            user = reu.user_real_estate_units.first()
            if not user:
                return None

        full_name = user.full_name
        if not full_name:
            first_name = "---"
            last_name = "---"
        else:
            space = full_name.find(" ")
            first_name = full_name[:space]
            last_name = full_name[space + 1 :]

        user_cells_1 = {
            "First Name": first_name,
            "Last Name": last_name,
            "Preferred Name": user.preferred_name,
            "Email": user.email,
        }

        return self._get_cells_from_dict(self.user_info_columns_1, user_cells_1)

    def _get_user_zipcodes(self, reus):
        zipcodes = ""
        for elem in reus:
            if getattr(elem, "address") and getattr(elem.address, "zipcode"):
                if zipcodes != "": 
                    zipcodes = zipcodes[:-1] + ", " + str(elem.address.zipcode) + "\""
                else: 
                    zipcodes += "=\"" +  str(elem.address.zipcode) + "\""

            elif getattr(elem, "location"):
                    location_list = elem.location.replace(", ", ",").split( ",")
                    zipc = location_list[-1]
                    if len(zipc) ==5 and zipc.isdigit():
                        if zipcodes != "": 
                            zipcodes = zipcodes[:-1] + ", " + str(zipc) + "\""
                        else: 
                            zipcodes+= "=\"" +  str(zipc) + "\""
        return zipcodes

    #Given user, returns last part of populated row (for Users CSV)
    def _get_user_info_cells_2(self, user):
        user_cells_2 = {}
        placeholder = ""

        if isinstance(user, Subscriber):
            user_cells_2 = {
                "Role": "Subscriber",
                "Created": user.created_at.strftime("%Y-%m-%d"),
                "Last sign in": placeholder,
            }

        elif isinstance(user, RealEstateUnit):
            # for geographic communities, list non-members who have households in the community
            reu = user
            user = reu.user_real_estate_units.first()
            if not user:
                return None

            #get city
            if reu.address and reu.address.city:
                city = reu.address.city
            else:
                city = "somewhere"
                # return None

            this_community = Community.objects.filter(id=self.community_id).first()
            # community list which user has associated with
            communities = [
                cm.community.name
                for cm in CommunityMember.objects.filter(user=user).select_related(
                    "community"
                )
            ]

            #get community
            if this_community.name in communities:
                return None
            elif len(communities) < 1:
                community = "NO COMMUNITY"
            elif len(communities) == 1:
                community = communities[0]
            else:
                community = str(communities)


            sign_in_date = user.visit_log[-1] if len(user.visit_log) >=1 else user.updated_at.strftime("%Y/%m/%d") if user.updated_at else placeholder

            user_cells_2 = {
                "Role": community + " member, household in " + city,
                "Created": user.created_at.strftime("%Y-%m-%d"),
                "Last sign in": str(sign_in_date),
            }

        else:
            is_guest = False
            if user.user_info:
                is_guest = (user.user_info.get("user_type", STANDARD_USER) == GUEST_USER)

            is_invited = not is_guest and not user.accepts_terms_and_conditions

            reus = user.real_estate_units.all()
            zipcodes = self._get_user_zipcodes(reus)

            sign_in_date = user.visit_log[-1] if len(user.visit_log) >=1 else user.updated_at.strftime("%Y/%m/%d") if user.updated_at else placeholder
            user_cells_2 = {
                "Zipcode": zipcodes,
                "Households (count)": reus.count(),
                "Role": "super admin"
                if user.is_super_admin
                else "community admin"
                if user.is_community_admin
                else "vendor"
                if user.is_vendor
                else "guest"
                if is_guest
                else "invited"
                if is_invited
                else "community member",
                "Created": user.created_at.strftime("%Y-%m-%d"),
                "Last sign in": sign_in_date,
            }

        return self._get_cells_from_dict(self.user_info_columns_2, user_cells_2)


    #Given a user and team, returns count and list of teams they are on, for Users CSV 
    def _get_team_info_for_user(self, user, teams):
        teams_for_user = teams.filter(teammember__user=user).values_list(
                "name", "teammember__is_admin"
            )
        tfu = []
        for team_name, is_admin in teams_for_user:
            tfu.append((team_name + "(ADMIN)") if is_admin else team_name)
        return teams_for_user.count(), tfu

    # Given a user, returns count of actions they've done and they've marked to-do, for Users CSV 
    def _get_action_counts_for_user(self, user):
        action_id_to_action_rel = {
                user_action_rel.action.id: user_action_rel
                for user_action_rel in UserActionRel.objects.filter(
                    is_deleted=False, user=user
                ).select_related("action")
            }

        todo_count = 0
        done_count= 0
        for elem in action_id_to_action_rel.values():
            if elem.status == "DONE":
                done_count += 1
            elif elem.status == "TODO":
                todo_count +=1
        return todo_count, done_count
        

    #Given information about users, actions and teams in a community, returns middle part of 
    #populated row (for Users CSV)
    def _get_user_actions_cells(self, user, actions, teams):
        user_cells = {}

        if isinstance(user, Subscriber) or isinstance(user, RealEstateUnit):
            #confirm REU has no testimonials, actions or teams (even though linked to a User?)
            user_cells = {}

        else:
            user_testimonials = Testimonial.objects.filter(is_deleted=False, user=user)
            testimonials_count = user_testimonials.count() if user_testimonials else "0"

            todo_count, done_count = self._get_action_counts_for_user(user)

            team_count, users_teams = self._get_team_info_for_user(user, teams)

            user_cells = {
                "Done (count)":done_count,
                "To-do (count)":todo_count,
                "Testimonials (count)": testimonials_count,
                "Teams (count)": team_count,
                "Teams": ', '.join(users_teams),
            }
        return self._get_cells_from_dict(self.user_info_columns_new, user_cells)
    
    # Receives an action, returns how many times it's been marked as Done in the last 30 days
    def _get_last_30_days_count(self, action):
        today = datetime.date.today()
        thirty_days_ago = today - timezone.timedelta(days = 30)

        done_actions_30_days = UserActionRel.objects.filter(
            is_deleted=False, action=action, status="DONE", date_completed__gte=thirty_days_ago,
        ) 

        return done_actions_30_days.count()

    #Gets row information for the All Actions CSV and the All Communities and Actions CSV
    def _get_action_info_cells(self, action):
        average_carbon_points = (
            AverageImpact(action.calculator_action)
            if action.calculator_action
            else int(action.average_carbon_score)
            if action.average_carbon_score.isdigit()
            else 0
        )

        is_published = "Yes" if action.is_published else "No"

        cc_action = action.calculator_action.name if action.calculator_action else ""

        category_obj = action.tags.filter(tag_collection__name="Category").first()
        category = category_obj.name if category_obj else None
        cost_obj = action.tags.filter(tag_collection__name="Cost").first()
        cost = cost_obj.name if cost_obj else None
        impact_obj = action.tags.filter(tag_collection__name="Impact").first()
        impact = impact_obj.name if impact_obj else None

        done_count = UserActionRel.objects.filter(
            is_deleted=False, action=action, status="DONE"
        ).count()
        total_carbon_points = average_carbon_points * done_count
        done_count = done_count

        todo_count = UserActionRel.objects.filter(
            is_deleted=False, action=action, status="TODO"
        ).count()

        testimonials_count = str(
            Testimonial.objects.filter(is_deleted=False, action=action).count()
        )

        done_in_last_30_days = self._get_last_30_days_count(action)


        action_cells = {
            "Live": is_published,
            "Action": action.title,
            "Done in last 30 days (count)": done_in_last_30_days,
            "Done (count)": done_count,
            "Annual GHG reduced per action (lbs)": average_carbon_points,
            "Total annual GHG reduced (lbs)": total_carbon_points,
            "To-do (count)": todo_count,
            "Testimonials (count)": testimonials_count,
            "Impact": impact,
            "Cost": cost,
            "Category": category,
            "Carbon Calculator Action": cc_action,
        }

        return self._get_cells_from_dict(self.action_info_columns, action_cells)

    #Given community, returns populated rows for state reported actions
    def _get_reported_data_rows(self, community):
        rows = []
        for action_category in self.action_categories:
            data = Data.objects.filter(tag=action_category, community=community).first()
            if not data:
                continue
            
            #doesn't include the row if the done count is 0
            if data.reported_value != 0: 
                rows.append(
                    self._get_cells_from_dict(
                        self.action_info_columns,
                        {
                            "Action": "STATE-REPORTED",
                            "Category": action_category.name,
                            "Done (count)": str(data.reported_value),
                        },
                    )
                )
        # if the done count for all STATE REPORTED actions in a community is 0, 
        # will show one row for that community with 0
      
        if len(rows) < 1:
            rows.append(self._get_cells_from_dict(self.action_info_columns,
                    {
                        "Action": "STATE-REPORTED",
                        "Done (count)": str(0),
                    },
                )
            )


        
                
        return rows

    #given members of a team, returns list of top 3 actions done the most in last 30 days 
    def _get_last_30_days_list(self, members):
        today = datetime.date.today()
        thirty_days_ago = today - timezone.timedelta(days = 30)
        top_actions ={}

        #makes dict with events that happened in last 30 days and how many times they happened!
        for user in members:
            actions = user.useractionrel_set.all()
            filtered = actions.filter(status="DONE", date_completed__gte = thirty_days_ago) #.values_list("action")
            for elem in filtered:
                top_actions[elem.action.title] = top_actions.get(elem.action.title, 0) + 1

        if len(top_actions) > 3:
            #sorts by number of times done, returns top three actions
            sorted_dict = dict(sorted(top_actions.items(), key=lambda item: item[1], reverse = True))
            return list(sorted_dict.keys())[0:3]

        return list(top_actions.keys())

    #Gets row information for the Teams CSV download
    def _get_team_info_cells(self, team):
        members = get_team_users(team)

        members_count = str(len(members))

        total_carbon_points = 0
        done_actions_count = 0
        todo_actions_count = 0
        for user in members:
            actions = user.useractionrel_set.all()
            
            done_actions = actions.filter(status="DONE")
            todo_actions_count += actions.filter(status= "TODO").count()
            done_actions_count += actions.filter(status= "DONE").count()

            for done_action in done_actions:
                if done_action.action and done_action.action.calculator_action:
                    total_carbon_points += (
                        AverageImpact(done_action.action.calculator_action, done_action.date_completed)
                    )
        total_carbon_points = str(total_carbon_points)

        trending_actions = self._get_last_30_days_list(members)

        testimonials_count = 0
        for user in members:
            testimonials_count += Testimonial.objects.filter(
                is_deleted=False, user=user
            ).count()
        testimonials_count = str(testimonials_count)

        team_cells = {
            "Team Name": team.name,
            "Members (count)": members_count,
            "Actions done (count)": done_actions_count,
            "To-do (count)": todo_actions_count,
            "Trending action(s)": ', '.join(trending_actions),
            "Testimonials (count)": testimonials_count,
            "Total annual GHG reduced (lbs)": total_carbon_points, 
            "Parent team": team.parent.name if team.parent else "",
        }
        return self._get_cells_from_dict(self.team_info_columns, team_cells)

    
    #Receives community, returns information about community to get row information for All Communities Download 
    def community_info_helper(self, community):
        community_members = CommunityMember.objects.filter(
            is_deleted=False, community=community
        ).select_related("user")

        teams_count = str(
            Team.objects.filter(is_deleted=False, primary_community=community).count()
        )
        events_count = str(
            Event.objects.filter(is_deleted=False, community=community).count()
        )
        actions_count = str(
            Action.objects.filter(is_deleted=False, community=community).count()
        )
        testimonials_count = str(
            Testimonial.objects.filter(is_deleted=False, community=community).count()
        )

        actions = (
            Action.objects.filter(Q(community=community) | Q(is_global=True))
            .filter(is_deleted=False)
            .select_related("calculator_action")
        )

        return community_members, teams_count, events_count, actions_count, testimonials_count, actions

    # Given users in community, returns most recent cadmin login date 
    def get_cadmin_recent_date(self, users):
        date_list = []
        for user in users:
            if user.is_community_admin:
                if len(user.visit_log) >=1:
                    date_list.append(user.visit_log[-1])
                date_list.append(user.updated_at.strftime("%Y/%m/%d"))

        return sorted(date_list)
    
    #Receives community, returns location of community if geographically focused
    def get_location_string(self, community):
        location_string = ""

        if community.is_geographically_focused:
            location_string += "["
            for loc in community.locations.all():
                if location_string != "[":
                    location_string += ","
                location_string += str(loc)
            location_string += "]"

            #uses old location value for community if newer one does not work
            if (location_string == "" or location_string == "[]") and community.location != None:
                location_string = str(community.location['city']) + ", " + str(community.location['state'])

        return location_string
    
    #Given a list of users for a community, returns the number of guests 
    def _get_guest_count(self, users):
        guest_count = 0
        for user in users:
            is_guest = False
            if user.user_info:
                is_guest = (user.user_info.get("user_type", STANDARD_USER) == GUEST_USER)
                if is_guest:
                    guest_count +=1
        return guest_count

    #given information about community and its users, returns information used to populate rows All Communities CSV 
    def _community_info_helper_2(self, community, users):
        if community.is_geographically_focused:
            # geographic focus - households are real estate units within the community (regardless of community membership)
            # actions are those associated with those households
            households_count = RealEstateUnit.objects.filter(
                is_deleted=False, community=community
            ).count()
            done_action_rels = UserActionRel.objects.filter(
                real_estate_unit__community=community, is_deleted=False, status="DONE"
            ).select_related("action__calculator_action")
            done_action_rels_members = UserActionRel.objects.filter(
                user__in=users, is_deleted=False, status="DONE"
            ).select_related("action__calculator_action")
        else:
            # non-geographic focus - households are real estate units of members, actions attributed to any community members
            households_count = sum([user.real_estate_units.count() for user in users])
            done_action_rels = UserActionRel.objects.filter(
                user__in=users, is_deleted=False, status="DONE"
            ).select_related("action__calculator_action")
            done_action_rels_members = done_action_rels
        return households_count, done_action_rels, done_action_rels_members
    
    def _get_primary_community_dict(self):
        
        users = UserProfile.objects.filter(is_deleted=False)

        comm_list = []
        for user in users:

                reu_community = None
                for reu in user.real_estate_units.all():
                    if reu.community:

                        comm_list.append(reu.community.name)
                        break
        
        return(Counter(comm_list))

    #Gets row information for each community for All Communities CSV
    def _get_community_info_cells(self, community, prim_comm_dict):
        
        location_string = self.get_location_string(community)

        community_members, teams_count, events_count, actions_count, testimonials_count, actions = self.community_info_helper(community)
        
        primary_community_user_count = 0
        if community.name in prim_comm_dict:
            primary_community_user_count = prim_comm_dict[community.name]

        users = [cm.user for cm in community_members]

        date_list = self.get_cadmin_recent_date(users)
        most_recent_cadmin_login = ""
        if len(date_list) >= 1:
            most_recent_cadmin_login = date_list[-1]      

        guest_count = self._get_guest_count(users)
        
        members_count = community_members.count()
        
        households_count, done_action_rels, done_action_rels_members = self._community_info_helper_2(community, users)
        
        actions_user_reported = done_action_rels.count()
        actions_of_members = done_action_rels_members.count()

        carbon_user_reported = sum(
            [
                AverageImpact(action_rel.action.calculator_action)
                if action_rel.action.calculator_action
                else 0
                for action_rel in done_action_rels
            ]
        )
        actions_per_member = (
            str(round(actions_of_members / members_count, 2))
            if members_count != 0
            else "0"
        )

        if not community.goal:
            # this may be the case for some bogus community like "Global", in which case make a temporary Goal
            community.goal = Goal()

        goal = community.goal
        actions_manual_addition = goal.initial_number_of_actions
        households_manual_addition = goal.initial_number_of_households
        carbon_manual_addition = goal.initial_carbon_footprint_reduction
        actions_partner = goal.attained_number_of_actions
        households_partner = goal.attained_number_of_households
        carbon_partner = goal.attained_carbon_footprint_reduction
        actions_total = (
            actions_user_reported + actions_manual_addition + actions_partner
        )
        households_total = (
            households_count + households_manual_addition + households_partner
        )
        carbon_total = carbon_user_reported + carbon_manual_addition + carbon_partner
        actions_goal = goal.target_number_of_actions
        households_goal = goal.target_number_of_households
        carbon_goal = goal.target_carbon_footprint_reduction
        actions_fraction = (
            round(actions_total / actions_goal, 2) if actions_goal > 0 else 0.0
        )
        households_fraction = (
            round(households_total / households_goal, 2) if households_goal > 0 else 0.0
        )
        carbon_fraction = (
            round(carbon_total / carbon_goal, 2) if carbon_goal > 0 else 0.0
        )

        geo_focused = "Yes" if community.is_geographically_focused else "No"

        community_cells = {
            "Community": community.name,
            "Location": location_string,
            "Geographically Focused": geo_focused,
            "Last Cadmin Login": str(most_recent_cadmin_login), 
            "Members (count)": str(members_count),
            "Primary Community Users (count)": str(primary_community_user_count), #first reu 
            "Guests (count)": str(guest_count),
            "Teams (count)": teams_count,
            "Actions (count)": str(actions_count),
            "Testimonials (count)": testimonials_count,
            "Events (count)": events_count,
            "Actions: User Reported": actions_user_reported,
            "Actions: Manual Addition": actions_manual_addition,
            "Actions: State/Partner Reported": actions_partner,
            "Actions: Total": actions_total,
            "Actions: Goal": actions_goal,
            "Actions: Goal Fraction": actions_fraction,
            "Households: User Reported": households_count,
            "Households: Manual Addition": households_manual_addition,
            "Households: State/Partner Reported": households_partner,
            "Households: Total": households_total,
            "Households: Goal": households_goal,
            "Households: Goal Fraction": households_fraction,
            "Carbon: User Reported": carbon_user_reported,
            "Carbon: Manual addition": carbon_manual_addition,
            "Carbon: State/Partner Reported": carbon_partner,
            "Carbon: Total": carbon_total,
            "Carbon: Goal": carbon_goal,
            "Carbon: Goal Fraction": carbon_fraction,
            "Actions per Member": actions_per_member,
        }

        return self._get_cells_from_dict(self.community_info_columns, community_cells)

    
    #Combines populated row and column information for all users overall to create All Users CSV
    def _all_users_download(self):
        users = list(UserProfile.objects.filter(is_deleted=False, 
                #accepts_terms_and_conditions=True
            )
        ) + list(Subscriber.objects.filter(is_deleted=False))
        actions = Action.objects.filter(is_deleted=False)
        teams = Team.objects.filter(is_deleted=False)

        columns = (
            self.user_info_columns_1 
            + ["home community", "secondary community"]
            + self.user_info_columns_new 
            + self.user_info_columns_2
        )

        data = []
        print("downloading " + str(len(users)) + " users")
        for user in users:
            if isinstance(user, Subscriber):
                if user.community:
                    primary_community, secondary_community = user.community.name, ""
                else:
                    primary_community, secondary_community = "", ""
            else:
                # community list which user has associated with
                communities = [
                    cm.community.name
                    for cm in CommunityMember.objects.filter(user=user).select_related(
                        "community"
                    )
                ]
                # communities of primary real estate unit associated with the user
                reu_community = None
                for reu in user.real_estate_units.all():
                    if reu.community:
                        reu_community = reu.community.name
                        break
                primary_community = secondary_community = ""
                # Primary community comes from a RealEstateUnit
                if reu_community:
                    primary_community = reu_community

                for community in communities:
                    if community != primary_community:
                        if secondary_community != "":
                            secondary_community += ", "
                        secondary_community += community
                # print(str(user) + ", " + str(len(communities)) + " communities, home is " + str(reu_community))

            row = (           
                self._get_user_info_cells_1(user)
                + [primary_community, secondary_community]
                + self._get_user_actions_cells(user, actions, teams)
                + self._get_user_info_cells_2(user)
            )
            data.append(row)

        # sort by community
        data = sorted(data, key=lambda row: row[0])
        # insert the columns
        data.insert(0, columns)
        return data

    # Combines populated row and column information for all users in a given community to create All Users CSV
    def _community_users_download(self, community_id):
        users = [
            cm.user
            for cm in CommunityMember.objects.filter(
                community__id=community_id,
                is_deleted=False,
                user__is_deleted=False,
                #user__accepts_terms_and_conditions=True,
            ).select_related("user")
        ] + list(
            Subscriber.objects.filter(community__id=community_id, is_deleted=False)
        )

        community_households = list(
            RealEstateUnit.objects.filter(community__id=community_id, is_deleted=False)
        )

        actions = Action.objects.filter(
            Q(community__id=community_id) | Q(is_global=True)
        ).filter(is_deleted=False)

        teams = Team.objects.filter(communities__id=community_id, is_deleted=False)

        columns = (
            self.user_info_columns_1 + self.user_info_columns_new + self.user_info_columns_2
        )
        data = [columns]

        for user in users:
            row = (
                self._get_user_info_cells_1(user)
                + self._get_user_actions_cells(user, actions, teams)
                + self._get_user_info_cells_2(user)
            )
            data.append(row)

        for household in community_households:
            if self._get_user_info_cells_2(household) is None:
                row = None
            else: 
                row = (self._get_user_info_cells_1(household)
                + ["" for _ in range(len(self.user_info_columns_new))]
                + self._get_user_info_cells_2(household)
            )
            if row:
                data.append(row)

        return data

    # based off of a method described as "new 1/11/20 BHN - untested"
    # Combines populated row and column information for all users on a given team to create All Users CSV
    def _team_users_download(self, team_id, community_id):

        users = [
            cm.user
            for cm in TeamMember.objects.filter(
                team__id=team_id,
                is_deleted=False,
                user__accepts_terms_and_conditions=True,
                user__is_deleted=False,
            ).select_related("user")
        ]

        # Soon teams could span communities, in which case actions list would be larger.
        # For now, take the primary community that a team is associated with; this may not be correct
        # TODO: loop over communities team is associated with and sort this all out
        
        team = Team.objects.get(id=team_id)

        teams = Team.objects.filter(is_deleted=False)
        community_id = team.primary_community.id
        actions = Action.objects.filter(
            Q(community__id=community_id) | Q(is_global=True)
        ).filter(is_deleted=False)

        columns = (
            self.user_info_columns_1 + self.user_info_columns_new + self.user_info_columns_2
        )

        data = [columns]
        for user in users:
            row = (
                self._get_user_info_cells_1(user)
                + self._get_user_actions_cells(user, actions, teams)
                + self._get_user_info_cells_2(user)
            )
            data.append(row)

        return data

    #Combines populated rows and columns to create All Communities an Actions CSV  - action data for all communities
    def _all_actions_download(self,community_ids=None):
        if community_ids:
            actions = Action.objects.filter(community__id__in=community_ids,is_deleted=False).select_related("calculator_action", "community").prefetch_related("tags")
        else:
            actions = (
                Action.objects.select_related("calculator_action", "community")
                .prefetch_related("tags")
                .filter(is_deleted=False)
            )

        columns = ["Community"] + ["Geographically Focused"] + self.action_info_columns
        data = []

        for action in actions:
            if not action.is_global and action.community:
                community = action.community.name
                is_focused = "Yes" if action.community.is_geographically_focused else "No"
            else:
                is_focused = community = ""
            data.append([community] + [is_focused] + self._get_action_info_cells(action))

        #get state reported actions
        communities = Community.objects.filter(is_deleted=False)
        for com in communities:
            community_reported_rows = self._get_reported_data_rows(com)
            for row in community_reported_rows:
                is_focused = "Yes" if com.is_geographically_focused else "No"
                data.append([com.name] + [is_focused] + row)

        
        data = sorted(data, key=lambda row: row[0])  # sort by community
        data.insert(0, columns)  # insert the column names
        return data

    #Combines populated rows and columns to create All Actions CSV  - action data for given community
    def _community_actions_download(self, community_id):
        actions = (
            Action.objects.filter(Q(community__id=community_id) | Q(is_global=True))
            .select_related("calculator_action")
            .prefetch_related("tags")
            .filter(is_deleted=False)
        )

        columns = self.action_info_columns
        data = [columns]
        for action in actions:
            data.append(self._get_action_info_cells(action))

        community = Community.objects.filter(id=community_id).first()
        community_reported_rows = self._get_reported_data_rows(community)
        for row in community_reported_rows:
            data.append(row)

        return data
    
    #Gets row and columns to create All Communities CSV data 
    def _all_communities_download(self):
        communities = Community.objects.filter(is_deleted=False)
        columns = self.community_info_columns
        data = [columns]

        primary_community_dict = self._get_primary_community_dict()

        for community in communities:
            data.append(self._get_community_info_cells(community,primary_community_dict))

        return data

    # Combines populated row and columns to create Teams CSV data 
    def _community_teams_download(self, community_id):
        teams = Team.objects.filter(communities__id=community_id, is_deleted=False)
        actions = Action.objects.filter(
            Q(community__id=community_id) | Q(is_global=True)
        ).filter(is_deleted=False)

        columns = self.team_info_columns
        data = [columns]

        for team in teams:
            data.append(
                self._get_team_info_cells(team)
            )

        return data
    
    
    def _action_users_download(self, action):
        user_action_rel = UserActionRel.objects.filter(action=action, is_deleted=False)
        columns = ["Recorded At","User", "Email", "Unit Name", "Unit Type", "Carbon Impact", "Status"]
        data = [columns]
        if len(user_action_rel) > 0:
            for user_action_rel in user_action_rel:
                cell  = self._get_cells_from_dict(columns,{
                    "Recorded At": get_human_readable_date(user_action_rel.created_at),
                    "User": user_action_rel.user.full_name,
                    "Email": user_action_rel.user.email,
                    "Unit Name": user_action_rel.real_estate_unit.name,
                    "Unit Type": user_action_rel.real_estate_unit.unit_type,
                    "Carbon Impact": user_action_rel.carbon_impact,
                    "Status": user_action_rel.status,
                })
                data.append(cell)
            return data
        else:
            return []
        
    
    def _actions_users_download(self, community_id):
        try:
            actions = Action.objects.filter(Q(community__id=community_id) | Q(is_global=True)).filter(is_deleted=False)
            user_action_rels = UserActionRel.objects.filter(is_deleted=False, action__in=actions).select_related("user", "action")
            
            if not user_action_rels:
                return []
            
            # format requested by Mike Roy + new requests
            columns = ["Action", "Completed On", "Full Name", "User Email", "Status"]
            data = [columns]

            # Group by action, then sort actions alphabetically
            action_to_rels = defaultdict(list)
            for rel in user_action_rels:
                action_to_rels[rel.action.title].append(rel)
            
            for action_title in sorted(action_to_rels.keys()):
                rels = action_to_rels[action_title]
                for action_rel in rels:
                    # Format date as mm/dd/yyyy (or blank if missing)
                    date_completed = ""
                    if action_rel.date_completed:
                        date_completed = action_rel.date_completed.strftime("%m/%d/%Y")
                    row = [
                        action_rel.action.title,
                        date_completed,
                        action_rel.user.full_name if action_rel.user else "",
                        action_rel.user.email if action_rel.user else "",
                        action_rel.status
                    ]
                    data.append(row)

            return data
        except Exception as e:
            log.exception(e)
            return []
    

    def _get_metrics_cells(self, community_id, time_stamp):

        metrics_cells = {
            "Is Live": time_stamp.is_live,
            "Households Total": time_stamp.households_total,
            "Households User Reported": time_stamp.households_user_reported,
            "Households Manual Addition": time_stamp.households_manual_addition,
            "Households Partner": time_stamp.households_partner,
            "Primary Community Users": time_stamp.primary_community_users_count,
            "Member Count": time_stamp.member_count,
            "Actions Live Count": time_stamp.actions_live_count,
            "Actions Total": time_stamp.actions_total,
            "Actions Partner": time_stamp.actions_partner,
            "Actions User Reported": time_stamp.actions_user_reported,
            "Carbon Total": time_stamp.carbon_total,
            "Carbon User Reported": time_stamp.carbon_user_reported,
            "Carbon Manual Addition": time_stamp.carbon_manual_addition,
            "Carbon Partner": time_stamp.carbon_partner,
            "Guest Count": time_stamp.guest_count,
            "Actions Manual Addition": time_stamp.actions_manual_addition,
            "Events Hosted Current": time_stamp.events_hosted_current,
            "Events Hosted Past": time_stamp.events_hosted_past,
            "My Events Shared Current": time_stamp.my_events_shared_current,
            "My Events Shared Past": time_stamp.my_events_shared_past,
            "Events Borrowed From Others Current": time_stamp.events_borrowed_from_others_current,
            "Events Borrowed From Others Past": time_stamp.events_borrowed_from_others_past,
            "Teams Count": time_stamp.teams_count,
            "Subteams Count": time_stamp.subteams_count,
            "Testimonials Count": time_stamp.testimonials_count,
            "Service Providers Count": time_stamp.service_providers_count,
            }

        return self._get_cells_from_dict(self.metrics_columns, metrics_cells)


    def _community_metrics_download(self, context, args, community_id):
        
        columns = ["Date"] + self.metrics_columns
        data = [columns]
        snapshots = CommunitySnapshot.objects.filter(community__id = community_id).order_by("date")

        for snap in snapshots:
            data.append([snap.date] + self._get_metrics_cells(community_id, snap))

        return data

    def _get_all_metrics_info_cells(self, snapshots, comms):
        dic = {"is_live": [], "households_total": 0, "households_user_reported": 0, "households_manual_addition":0,
        "households_partner":0, "primary_community_users_count":0, "member_count":0, "actions_live_count":0,
        'actions_total':0, 'actions_partner':0, 'actions_user_reported':0,
        'carbon_total':0.0, 'carbon_user_reported':0.0, 'carbon_manual_addition':0.0,
        'carbon_partner':0.0, 'guest_count':0, 'actions_manual_addition':0,
        'events_hosted_current':0, 'events_hosted_past':0, 'my_events_shared_current':0,
        'my_events_shared_past':0, 'events_borrowed_from_others_current':0,
        'events_borrowed_from_others_past':0, 'teams_count':0, 'subteams_count':0,
        'testimonials_count':0, 'service_providers_count':0,
        }
        snapshots_list = [] 
        comms_list =[]
        #if more than one timestamp for a given community on certain date, get latest one
        for elem in comms:
            # in dev database avoid some bad data
            if not elem[0]:
                continue
            stamp = snapshots.filter(community__id = elem[0]).order_by("-date").first()
            snapshots_list.append(stamp)
            comms_list.append(stamp.community.name)

        #for each field in CSV, sum value across all relevant snapshots
        for key in dic.keys():
            for stamp in snapshots_list:

                if key == "is_live":
                    if getattr(stamp, key) == True:
                        dic[key] = dic[key] + [stamp.community.name]

                else:
                    if not getattr(stamp, key):
                        continue
                    field_value = getattr(stamp, key)
                    #adds values as floats or ints, depending on category
                    if key == "carbon_total" or key == "carbon_user_reported" or key == "carbon_manual_addition" or key == "carbon_partner":
                        dic[key] = dic[key] + float(field_value)
                    else:
                        dic[key] = dic[key] + int(field_value)

        dic["is_live"].sort()
        metrics_cells = {
            "Is Live": ', '.join(dic["is_live"]),
            "Households Total": dic["households_total"],
            "Households User Reported": dic["households_user_reported"],
            "Households Manual Addition": dic["households_manual_addition"],
            "Households Partner": dic["households_partner"],
            "Primary Community Users": dic["primary_community_users_count"],
            "Member Count": dic["member_count"],
            "Actions Live Count": dic["actions_live_count"],
            "Actions Total": dic["actions_total"],
            "Actions Partner": dic["actions_partner"],
            "Actions User Reported": dic["actions_user_reported"],
            "Carbon Total": dic["carbon_total"],
            "Carbon User Reported": dic["carbon_user_reported"],
            "Carbon Manual Addition": dic["carbon_manual_addition"],
            "Carbon Partner": dic["carbon_partner"],
            "Guest Count": dic["guest_count"],
            "Actions Manual Addition": dic["actions_manual_addition"],
            "Events Hosted Current": dic["events_hosted_current"],
            "Events Hosted Past": dic["events_hosted_past"],
            "My Events Shared Current": dic["my_events_shared_current"],
            "My Events Shared Past": dic["my_events_shared_past"],
            "Events Borrowed From Others Current": dic["events_borrowed_from_others_current"],
            "Events Borrowed From Others Past": dic["events_borrowed_from_others_past"],
            "Teams Count": dic["teams_count"],
            "Subteams Count": dic["subteams_count"],
            "Testimonials Count": dic["testimonials_count"],
            "Service Providers Count": dic["service_providers_count"],
            }

        return self._get_cells_from_dict(self.metrics_columns, metrics_cells), comms_list, len(dic["is_live"])

    
    def _all_metrics_download(self, context, args):
        columns = ["Date", " # Communities", "# Live"] + self.metrics_columns + ["Communities"]
        data = [columns]
        audience = args["audience"]
        comm_ids = []
        if args.get("community_ids"):
            comm_ids = args["community_ids"].split(",")
        if audience == "SPECIFIC":
            community_snapshots = CommunitySnapshot.objects.filter(community__id__in = comm_ids).order_by("date")
        elif audience == "ALL_EXCEPT":
            community_snapshots = CommunitySnapshot.objects.exclude(community__id__in = comm_ids).order_by("date")
        else:
            community_snapshots = CommunitySnapshot.objects.filter().order_by("date")

        distinct_dates = community_snapshots.values_list("date").distinct() 

        #for every date make a row in the CSV
        for elem in distinct_dates:
            snapshots_list = community_snapshots.filter(date = elem[0])
            comm_ids = snapshots_list.values_list("community").distinct()
            most_info, comms_list, live_num = self._get_all_metrics_info_cells(snapshots_list, comm_ids)
            comms_list.sort()
            data.append([elem[0]] + [len(comms_list)] + [live_num] + most_info + [', '.join(comms_list)])

        return data

    def _fill_pagemap_header(self, community):
        data = []

        line = community.name + " page map"	
        data.append(line)
        today = datetime.date.today()
        line = "Generated: " + str(today)
        data.append(line)
        data.append("")			
        return data
    
    def _get_pagemap_data(self, community):
        data = []

        #Home page
        customDomain = CustomCommunityWebsiteDomain.objects.filter(community__id=community.id)
        if customDomain:
            communityURL = 'https://'+customDomain.first().website
        else:
            communityURL = f'{COMMUNITY_URL_ROOT}/{community.subdomain}'

        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/community/community-admin'
        pagedata = {"Page Name":hyperlink("Home Page", communityURL),
                    "Status":"Enabled",  
                    "Admin Page Name":hyperlink("Community Information",adminURL),
                    }
        data.append(pagedata)

        #Community profile
        adminURL = f'{ADMIN_URL_ROOT}/admin/community/{community.id}/profile'
        pagedata = {"Admin Page Name":hyperlink("Community Profile",adminURL),
                    }
        data.append(pagedata)

        #Community admins
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/community-admins'
        pagedata = {"Admin Page Name":hyperlink("Community Admins",adminURL),
                    }
        data.append(pagedata)

        #Home page settings
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/home'
        pageSettings = HomePageSettings.objects.get(community__id=community.id)
        pagedata = {"Admin Page Name":hyperlink("Home Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        #Goals and impact data
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/impacts'
        pagedata = {"Admin Page Name":hyperlink("Goals and Impact Data",adminURL),
                    }
        data.append(pagedata)

        #Impact page
        pageSettings = ImpactPageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/impact'
        pagedata = {"Page Name":hyperlink("Impact Page", communityURL+'/impact'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("Impact Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        #AboutUs page
        pageSettings = AboutUsPageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/about'
        pagedata = {"Page Name":hyperlink("AboutUs Page",communityURL+'/aboutus'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("AboutUs Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        #Donate Page
        pageSettings = DonatePageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/donate'
        pagedata = {"Page Name":hyperlink("Donate Page",communityURL+'/donate'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("Donate Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        #ContactUs Page
        pageSettings = ContactUsPageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/contact_us'
        pagedata = {"Page Name":hyperlink("ContactUs Page",communityURL+'/contactus'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("ContactUs Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        #All Actions Page
        pageSettings = AboutUsPageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/all-actions'
        pagedata = {"Page Name":hyperlink("All Actions Page",communityURL+'/actions'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("Actions Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        # individual action pages
        actions = Action.objects.filter(community__id=community.id, is_deleted=False)
        for action in actions:
            status = "Published" if action.is_published else ""
            adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{action.id}/action'
            pagedata = {"Page Name":hyperlink(action.title,communityURL+'/actions/'+str(action.id)), 
                        "Status": status,  
                        "Admin Page Name":hyperlink("Edit Action Content",adminURL),
                        "Updated on":update_date(action),
                        "Updated by":update_user(action),
                        }
            data.append(pagedata)

        #All Events Page
        pageSettings = EventsPageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/all-events'
        pagedata = {"Page Name":hyperlink("All Events Page",communityURL+'/events'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("Events Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        # individual event pages
        events = Event.objects.filter(community__id=community.id, is_deleted=False)
        for event in events:
            status = "Published" if action.is_published else ""
            adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{action.id}/event'
            pagedata = {"Page Name":hyperlink(event.name,communityURL+'/events/'+str(action.id)), 
                        "Status": status,  
                        "Admin Page Name":hyperlink("Edit Event Content",adminURL),
                        "Updated on":update_date(event),
                        "Updated by":update_user(event),
                        }
            data.append(pagedata)

        #All Testimonials Page
        pageSettings = TestimonialsPageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/all-testimonials'
        pagedata = {"Page Name":hyperlink("All Testimonials Page",communityURL+'/testimonials'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("Testimonials Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        # individual testimonial pages
        items = Testimonial.objects.filter(community__id=community.id, is_deleted=False)
        for item in items:
            status = "Published" if item.is_published else ""
            adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{item.id}/testimonial'
            pagedata = {"Page Name":hyperlink(item.title,communityURL+'/testimonials/'+str(item.id)), 
                        "Status": status,  
                        "Admin Page Name":hyperlink("Edit Testimonial Content",adminURL),
                        "Updated on":update_date(item),
                        "Updated by":update_user(item),
                        }
            data.append(pagedata)

        #All Service Providers page
        pageSettings = VendorsPageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edity/{community.id}/all-vendors'
        pagedata = {"Page Name":hyperlink("All Services Page",communityURL+'/services'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("Services Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        #individual service provider pages
        items = Vendor.objects.filter(communities__id=community.id, is_deleted=False)
        for item in items:
            status = "Published" if item.is_published else ""
            adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{item.id}/vendor'
            pagedata = {"Page Name":hyperlink(item.name,communityURL+'/services/'+str(item.id)), 
                        "Status": status,  
                        "Admin Page Name":hyperlink("Edit Service Content",adminURL),
                        "Updated on":update_date(item),
                        "Updated by":update_user(item),
                    }
            data.append(pagedata)


        #All Teams page
        pageSettings = TeamsPageSettings.objects.get(community__id=community.id)
        status = "Enabled" if pageSettings.is_published else "Disabled"
        adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{community.id}/all-teams'
        pagedata = {"Page Name":hyperlink("All Teams Page",communityURL+'/teams'), 
                    "Status": status,  
                    "Admin Page Name":hyperlink("Teams Page Settings",adminURL),
                    "Updated on":update_date(pageSettings),
                    }
        data.append(pagedata)

        # individual teams pages
        items = Team.objects.filter(primary_community__id=community.id, is_deleted=False)
        for item in items:
            status = "Published" if item.is_published else ""
            adminURL = f'{ADMIN_URL_ROOT}/admin/edit/{item.id}/team'
            pagedata = {"Page Name":hyperlink(item.name,communityURL+'/teams/'+str(item.id)), 
                        "Status": status,  
                        "Admin Page Name":hyperlink("Edit Team Content",adminURL),
                        "Updated on":update_date(item),
                        "Updated by":update_user(item),
                        }
            data.append(pagedata)
        return data

    def _fill_pagemap_cells(self, pagedata):
        return self._get_cells_from_dict(self.pagemap_columns, pagedata)



    def _community_pagemap_download(self, context, community_id):

        community = Community.objects.get(id=community_id)

        data = [self._fill_pagemap_header(community)]
        data.append([])

        # column titles
        columns = self.pagemap_columns

        data.append(columns)

        pages = self._get_pagemap_data(community)
        for page in pages:
            row = self._fill_pagemap_cells(page)
            data.append(row)
        return data


    # For All Users CSV -- all users for a given team, or all users for a given community, or (for superadmins) all users overall 
    def users_download(
        self, context: Context, community_id, team_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            self.community_id = community_id
            if team_id:
                community_name = Team.objects.get(id=team_id).name
            elif community_id:
                community_name = Community.objects.get(id=community_id).name

            if context.user_is_super_admin:
                if team_id:
                    #All Users CSV method for all users in a given team
                    return (self._team_users_download(team_id, community_id), community_name), None 
                elif community_id:
                    #All Users CSV method for all users in a given community
                    return (self._community_users_download(community_id), community_name), None
                else:
                    #All Users CSV method for all users overall
                    return (self._all_users_download(), None), None
            elif context.user_is_community_admin:
                if not is_admin_of_community(context, community_id):
                    return EMPTY_DOWNLOAD, NotAuthorizedError()
                if team_id:
                    #All Users CSV method for all users in a given team
                    return (self._team_users_download(team_id, community_id), community_name), None
                elif community_id:
                    #All Users CSV method for all users in a given community
                    return (
                        self._community_users_download(community_id),
                        community_name,
                    ), None
                else:
                    return EMPTY_DOWNLOAD, NotAuthorizedError()
            else:
                return EMPTY_DOWNLOAD, NotAuthorizedError()
        except Exception as e:
            print(str(e))
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        


 
    #For All Actions CSV and (for superadmins) the All Communities and Actions CSV
    def actions_download(
        self, context: Context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            self.community_id = community_id
            if community_id:
                if not is_admin_of_community(context, community_id):
                    return EMPTY_DOWNLOAD, NotAuthorizedError()
                community_name = Community.objects.get(id=community_id).name
                return (
                    #All Actions CSV method - action data for one community
                    self._community_actions_download(community_id),
                    community_name,
                ), None
            elif context.user_is_super_admin or context.user_is_community_admin:
                #All Communities and Actions CSV method - action data across all communities
                return (self._all_actions_download(), None), None
            else:
                return EMPTY_DOWNLOAD, NotAuthorizedError()
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

    #For All Communities CSV - for superadmin, information about each community
    def communities_download(
        self, context: Context
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_super_admin:
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            return (self._all_communities_download(), None), None
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

    #For Teams CSV --  information about the Teams in a given community
    def teams_download(
        self, context: Context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        self.community_id = community_id
        try:
            # Allow this download only if the user is a community admin and an admin to the community or a superadm
            if not is_admin_of_community(context, community_id):
                return EMPTY_DOWNLOAD, NotAuthorizedError()

            community = Community.objects.get(id=community_id)
            if community:
                return (
                    self._community_teams_download(community.id),
                    community.name,
                ), None
            else:
                return EMPTY_DOWNLOAD, InvalidResourceError()
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)


    def metrics_download(
        self, context: Context, args, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            if community_id: 
                if not is_admin_of_community(context, community_id):
                    return EMPTY_DOWNLOAD, NotAuthorizedError()
                community_name = Community.objects.get(id=community_id).name
                return (
                    self._community_metrics_download(context, args, community_id),
                    community_name,
                ), None
            elif context.user_is_super_admin:
                return (
                    self._all_metrics_download(context, args), 
                    None,), None
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    # download data on an individual action and users who taken it
    def action_users_download(self, context: Context, action_id) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            
            action = Action.objects.filter(id=action_id, is_deleted=False).first()
            if not action:
                return EMPTY_DOWNLOAD, InvalidResourceError()

            action_users_data = self._action_users_download(action)
            if len(action_users_data) == 0:
                return EMPTY_DOWNLOAD, InvalidResourceError()
            
            return (action_users_data, action.title), None

        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

    # download information on actions from a community and users who've recorded then        
    def actions_users_download(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            
            community = Community.objects.filter(id=community_id, is_deleted=False).first()
            if not community:
                return EMPTY_DOWNLOAD, InvalidResourceError()

            action_users_data = self._actions_users_download(community_id)
            if len(action_users_data) == 0:
                return EMPTY_DOWNLOAD, InvalidResourceError()
            
            return (action_users_data, community.name), None
            
            
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    def community_pagemap_download(
        self, context: Context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            if community_id: 
                return (
                    self._community_pagemap_download(context, community_id),
                    None,
                ), None
            else:
                return EMPTY_DOWNLOAD, NotAuthorizedError()
        except Exception as e:
            print("community_pagemap_exception: " + str(e))
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    
    def _campaign_follows_download(self, campaign):
        columns = ["Date", "Email", "Community", "Zipcode", "From_Other_Community"]

        def get_community_name(follow):
            if follow.community:
               if follow.community.name != "Other":
                    return follow.community.name
               else:
                return follow.community_name
            return "N/A"
        
        def get_zipcode(follow):
            try:
                if follow.zipcode:
                    return follow.zipcode
                elif not follow.community_name:
                    location = follow.community.locations.first() if follow.community and follow.community.locations else None
                    zipcode = location.zipcode if location else "N/A"
                    return zipcode
                return "N/A"
            except Exception as e:
                print(f"An error occurred: {e}")
                return "N/A"
        # 
        data = [columns]
        follows = CampaignFollow.objects.filter(campaign=campaign, is_deleted=False)
        for follow in follows:
            cell  = self._get_cells_from_dict(columns,{
                "Date": get_human_readable_date(follow.created_at),
                "Email": follow.user.email,
                "Community": get_community_name(follow),
                "Zipcode": get_zipcode(follow),
                "From_Other_Community": "Yes" if follow.community_name else "No",
            })
            data.append(cell)
        return data
        


    def campaign_follows_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            
            campaign = Campaign.objects.filter(id=campaign_id, is_deleted=False).first()
            if not campaign:
                return EMPTY_DOWNLOAD, InvalidResourceError()
            
            return (self._campaign_follows_download(campaign), None), None
            
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        


        
    def _campaign_likes_download(self, campaign):
        columns = ["Date", "Email", "Community",  "Technology", "Zipcode"]

        def get_community_name(like):
            if like.community:
               if like.community.name != "Other":
                    return like.community.name
               else:
                return like.community_name
            return "N/A"
        
        def get_zipcode(like):
            if like.zipcode:
                return like.zipcode
            elif not like.community_name:
                zipcode = like.community.locations.first().zipcode if like.community and like.community.locations else "N/A"
                return zipcode
                
            return "N/A"
        # 
        data = [columns]
        likes = CampaignTechnologyLike.objects.filter(campaign_technology__campaign__id=campaign.id, is_deleted=False)
        for like in likes:
            cell  = self._get_cells_from_dict(columns,{
                "Date": get_human_readable_date(like.created_at),
                "Email": like.user.email if like.user else "N/A",
                "Community": get_community_name(like),
                "Technology": like.campaign_technology.technology.name,
                "Zipcode": get_zipcode(like),
            })
            data.append(cell)
        return data    
        

    def campaign_likes_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            
            campaign = Campaign.objects.filter(id=campaign_id, is_deleted=False).first()
            if not campaign:
                return EMPTY_DOWNLOAD, InvalidResourceError()
            
            return (self._campaign_likes_download(campaign), None), None
            
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
    

    def _campaign_link_performance_download(self,campaign):
        columns = ["Date", "Campaign", "Email",  "Source", "Medium", "Click Count"]
        data = [columns]
        clicks = CampaignLink.objects.filter(campaign__id=campaign.id, is_deleted=False)
        for click in clicks:
            cell  = self._get_cells_from_dict(columns,{
                "Date": get_human_readable_date(click.created_at),
                "Email": click.email,
                "Source": click.utm_source,
                "Medium": click.utm_medium,
                "Click Count": click.visits,
            })
            data.append(cell)
        return data

    
    def campaign_link_performance_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            
            campaign = Campaign.objects.filter(id=campaign_id, is_deleted=False).first()
            if not campaign:
                return EMPTY_DOWNLOAD, InvalidResourceError()
            
            return (self._campaign_link_performance_download(campaign), None), None
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    def campaign_views_performance_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            
            campaign = Campaign.objects.filter(id=campaign_id, is_deleted=False).first()
            if not campaign:
                return EMPTY_DOWNLOAD, InvalidResourceError()
            
            columns = ["Date", "Campaign", "Technology",  "Email"]
            data = [columns]
            views = CampaignTechnologyView.objects.filter(campaign_technology__campaign__id=campaign_id, is_deleted=False)
            for view in views:
                cell  = self._get_cells_from_dict(columns,{
                    "Campaign": view.campaign_technology.campaign.title,
                    "Technology": view.campaign_technology.technology.name,
                    "Email": view.email,
                })
                data.append(cell)
            return (data, None), None
            
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        


    def _campaign_interaction_performance_download(self, campaign):
        columns = ["Date", "Email",  "Source", "Element", "Target"]
        data = [columns]
        interactions = CampaignActivityTracking.objects.filter(campaign__id=campaign.id, is_deleted=False)
        for interaction in interactions:
            cell  = self._get_cells_from_dict(columns,{
                "Date": get_human_readable_date(interaction.created_at),
                "Source": interaction.source,
                "Email": interaction.email,
                "Target": interaction.target,
                "Element": interaction.button_type
                
            })
            data.append(cell)
        return data

    def campaign_interaction_performance_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            
            campaign = Campaign.objects.filter(id=campaign_id, is_deleted=False).first()
            if not campaign:
                return EMPTY_DOWNLOAD, InvalidResourceError()
            return (self._campaign_interaction_performance_download(campaign), None), None
            
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    

    def _campaign_overview_download(self, campaign):
        columns = ["Metric", "Value"]
        data = [columns]

        likes = CampaignTechnologyLike.objects.filter(campaign_technology__campaign__id=campaign.id, is_deleted=False).aggregate(total_likes=Sum('count'))['total_likes']
        follows = CampaignFollow.objects.filter(campaign__id=campaign.id, is_deleted=False).count()
        views = CampaignTechnologyView.objects.filter(campaign_technology__campaign__id=campaign.id, is_deleted=False).aggregate(total_views=Sum('count'))['total_views']
        campaign_views = CampaignView.objects.filter(campaign__id=campaign.id, is_deleted=False).aggregate(total_views=Sum('count'))['total_views']
        comments = Comment.objects.filter(campaign_technology__campaign__id=campaign.id, is_deleted=False).count()
        shares = CampaignLink.objects.filter(campaign__id=campaign.id, is_deleted=False).count()
        testimonials = CampaignTechnologyTestimonial.objects.filter(campaign_technology__campaign__id=campaign.id, is_deleted=False).count()

        rows = [
            ["Total Likes", likes],
            ["Total Follows", follows],
            ["Total Views", campaign_views],
            ["Total Technology Views", views],
            ["Total comments", comments],
            ["Total Shares", shares],
            ["Total testimonials", testimonials],
        ]

        data += [self._get_cells_from_dict(columns, {"Metric": row[0], "Value": row[1]}) for row in rows]

        techs = CampaignTechnology.objects.filter(campaign__id=campaign.id, is_deleted=False)
        for tech in techs:
            likes = CampaignTechnologyLike.objects.filter(campaign_technology__id=tech.id, is_deleted=False).aggregate(total_likes=Sum('count'))['total_likes']
            follows = CampaignTechnologyFollow.objects.filter(campaign_technology__id=tech.id, is_deleted=False).count()
            views = CampaignTechnologyView.objects.filter(campaign_technology__id=tech.id, is_deleted=False).aggregate(total_views=Sum('count'))['total_views']
            comments = Comment.objects.filter(campaign_technology__id=tech.id, is_deleted=False).count()
            testimonials = CampaignTechnologyTestimonial.objects.filter(campaign_technology__id=tech.id, is_deleted=False).count()

            rows = [
                ["Total Likes", likes or 0],
                ["Total Follows", follows or 0],
                ["Total Views", views or 0],
                ["Total comments", comments or 0],
                ["Total testimonials", testimonials or 0],
            ]

            data.append([])
            data.append([])
            data.append(["Technology", tech.technology.name])
            data += [self._get_cells_from_dict(columns, {"Metric": row[0], "Value": row[1]}) for row in rows]

        return data
    


    def _get_performance_data_for_community(self, community, campaign):
        try:
           
            follows = CampaignFollow.objects.filter(campaign__id=campaign.id, community__id=community.id, is_deleted=False)
            likes = CampaignTechnologyLike.objects.filter(campaign_technology__campaign__id=campaign.id, community__id=community.id, is_deleted=False).first()
            comments = Comment.objects.filter(campaign_technology__campaign__id=campaign.id, community__id=community.id, is_deleted=False).count()
            testimonials = CampaignTechnologyTestimonial.objects.filter(campaign_technology__campaign__id=campaign.id, testimonial__community__id=community.id, is_deleted=False).count()
            rows = [
                ["Total Follows",follows.count() if follows else 0],
                ["Total Likes", likes.count if likes else 0],
                ["Total comments", comments],
                ["Total testimonials", testimonials],
            ]

            columns = ["Metric", "Value"]
            data = [columns]
            data += [self._get_cells_from_dict(columns, {"Metric": row[0], "Value": row[1]}) for row in rows]

            # show th list of followers

            if follows:
                data.append([])
                data.append([])
                data.append(["Followers"])
                columns = ["Date", "Email", "Community", "Zipcode", "From_Other_Community"]
                data.append(columns)

                for follower in follows:
                    cell  = self._get_cells_from_dict(columns,{
                        "Date": get_human_readable_date(follower.created_at),
                        "Email": follower.user.email,
                        "Community": follower.community.name,
                        "Zipcode": follower.zipcode,
                        "From_Other_Community": "Yes" if follower.community_name else "No",
                    })
                    data.append(cell)
            return data

        
        except Exception as e:
            print("error: " + str(e))
            return []

        


    def campaign_performance_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()

            campaign = None
            try:
                uuid_id = UUID(campaign_id, version=4)
                campaign = Campaign.objects.filter(id=uuid_id, is_deleted=False).first()
            except ValueError:
                campaign = Campaign.objects.filter(slug=campaign_id, is_deleted=False).first()

            if not campaign:
                return EMPTY_DOWNLOAD, CustomMassenergizeError("Campaign not found")

            sheet_data = {}
            sheet_data["Campaign Overview"] = {
                "data": self._campaign_overview_download(campaign)
            }
            sheet_data["Campaign Follows"] = {
                "data": self._campaign_follows_download(campaign)
            }

            sheet_data["Campaign Link Performance"] = {
                "data": self._campaign_link_performance_download(campaign)
            }
            
            sheet_data["Campaign Interaction Performance"] = {
                "data": self._campaign_interaction_performance_download(campaign)
            }
            # create sheet for ech community in the campaign
            communities = campaign.campaign_community.filter(is_deleted=False)

            for community in communities:
                sheet_data[f"{community.community.name}"] = {
                    "data": self._get_performance_data_for_community(community.community,campaign)
                }

            wb =generate_workbook_with_sheets(sheet_data)

            return (wb, campaign.title), None
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    def export_actions(self, context: Context, community_id=None) -> Tuple[list, MassEnergizeAPIError]:
        try:      
            if not community_id:     
                return (self._export_all_actions(), "All Actions"), None              
            community_name = Community.objects.get(id=community_id).name
            return (self._export_community_actions(community_id), community_name), None

        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

    def export_events(self, context: Context, community_id=None) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not community_id:
                return (self._export_all_events_for_wp(), "All Events"), None
            
            community_name = Community.objects.get(id=community_id).name
            return (self._export_all_events_for_wp(community_id), community_name), None
  
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

    def export_testimonials(self, context: Context, community_id=None) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not community_id:
                return (self._export_all_testimonials(), "All Testimonials"), None
            community_name = Community.objects.get(id=community_id).name
            return (self._community_testimonials_download(community_id), community_name), None
   
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    def export_vendors(self, context: Context, community_id=None) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not community_id:
                    return EMPTY_DOWNLOAD, CustomMassenergizeError("Please provide community_id")  
            community_name = Community.objects.get(id=community_id).name
            return (self._community_vendors_download(community_id), community_name), None
   
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    def export_cc_actions(self, context: Context, community_id=None) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not community_id:
                    return EMPTY_DOWNLOAD, CustomMassenergizeError("Please provide community_id")
            community_name = Community.objects.get(id=community_id).name
            return (self._cc_actions_download(community_id), community_name), None
        except Exception as e:
            log.exception(e)
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
        

    def _cc_actions_download(self, community_id):
        actions = CCAction.objects.all()
        columns = ["Name", "Title", "Category", "Sub Category", "Description", "Average Points"]

        data = [columns]
        for action in actions:
            cell = self._get_cells_from_dict(columns, {
                "Name": action.name,
                "Title": action.title,
                "Category": action.category.name if action.category else "",
                "Sub Category": action.sub_category.name if action.sub_category else "",
                "Description": action.description,
                "Average Points": action.average_points
            })
            data.append(cell)
        return data

        

    def _community_vendors_download(self, community_id):
        vendors = Vendor.objects.filter(communities__id=community_id, is_deleted=False, is_published=True)
        columns = ["Name", "Logo", "Description", "Website", "Key Contact", "Key Contact Email", "Communities Serviced", "Service Area"]
        data = [columns]
        for vendor in vendors:
            image_url = vendor.logo.file.url if vendor.logo else ""
            compressed_image_url = self._get_compressed_image_url(image_url)
            key_contact = vendor.key_contact or {}
            cell = self._get_cells_from_dict(columns, {
                "Name": vendor.name,
                "Logo": compressed_image_url,
                "Description": vendor.description,
                "Website": vendor.get_field_from_more_info("website"),
                "Key Contact": key_contact.get("name") if key_contact else "",
                "Key Contact Email": key_contact.get("email") if key_contact else "",
                "Communities Serviced": ", ".join([community.name for community in vendor.communities.all()]),
                "Service Area": vendor.service_area,
            })
            data.append(cell)
        return data
    

    def _community_events_download(self, community_id):
        events = Event.objects.filter(community__id=community_id, is_deleted=False, is_published=True)
        columns = ["Title", "Description", "Start Date", "End Date", "Location", "Event Type", "Link", "Image", "Tags"]
        data = [columns]
        
        for event in events:
            image_url = event.image.file.url if event.image else ""
            compressed_image_url = self._get_compressed_image_url(image_url)
            cell = self._get_cells_from_dict(columns, {
                "Title": event.name,
                "Description": event.description,
                "Start Date": get_massachusetts_time(event.start_date_and_time).strftime("%Y-%m-%d %H:%M") if event.start_date_and_time else "",
                "End Date": get_massachusetts_time(event.end_date_and_time).strftime("%Y-%m-%d %H:%M") if event.end_date_and_time else "",
                "Location": event.location,
                "Event Type": event.event_type,
                "Link": event.external_link if event.external_link else "",
                "Image": compressed_image_url if event.image else "",
                "Tags": ", ".join([tag.name for tag in event.tags.all()])
            })
            data.append(cell)
        return data


    def _community_testimonials_download(self, community_id):
        testimonials = Testimonial.objects.filter(community__id=community_id, is_deleted=False, is_published=True)
        columns = ["Title", "Body","User","Related Action", "Related Vendor", "Image", "Tags",  "Email"]
        data = [columns]
        
        for testimonial in testimonials:
            image_url = testimonial.image.file.url if testimonial.image else ""
            compressed_image_url = self._get_compressed_image_url(image_url)
            cell = self._get_cells_from_dict(columns, {
                "Title": testimonial.title,
                "Body": testimonial.body,
                "User": testimonial.user.full_name if testimonial.user else testimonial.preferred_name or "",
                "Related Action": testimonial.action.title if testimonial.action else "",
                "Related Vendor": testimonial.vendor.name if testimonial.vendor else "",
                "Image": compressed_image_url,
                "Tags": ", ".join([f"{tag.name}:{tag.tag_collection.name if tag.tag_collection else ''}" for tag in testimonial.tags.all()]),
                "Email": testimonial.user.email if testimonial.user else ""
            })
            data.append(cell)
        return data
    
    def _export_community_actions(self, community_id):
        actions = Action.objects.filter(community__id=community_id, is_deleted=False,is_published=True)
        columns = ["Title", "Description", "Steps to Take", "Deep Dive", "Image", "CC Action", "Tags"]
        data = [columns]
        
        for action in actions:
            image_url = action.image.file.url if action.image else ""
            compressed_image_url = self._get_compressed_image_url(image_url)
            tags = action.tags.all()
            cell = self._get_cells_from_dict(columns, {
                "Title": action.title,
                "Description": action.about,
                "Steps to Take": action.steps_to_take,
                "Deep Dive": action.deep_dive,
                "Image": compressed_image_url,
                "CC Action": action.calculator_action.name if action.calculator_action else "",
                "Tags": ", ".join([f"{tag.name}:{tag.tag_collection.name if tag.tag_collection else ''}" for tag in action.tags.all()])
            })
            data.append(cell)
        return data
        

    def _export_all_actions(self):
        actions = Action.objects.filter(is_deleted=False,is_published=True)
        columns = ["Title", "Description", "Steps to Take", "Deep Dive", "Image", "CC Action", "Tags", "Community"]
        data = [columns]

        for action in actions:
            image_url = action.image.file.url if action.image else ""
            compressed_image_url = self._get_compressed_image_url(image_url)

            cell = self._get_cells_from_dict(columns, {
                "Title": action.title,
                "Description": action.about,
                "Steps to Take": action.steps_to_take,
                "Deep Dive": action.deep_dive,
                "Image": compressed_image_url,
                "CC Action": action.calculator_action.name if action.calculator_action else "",
                "Tags": ", ".join([f"{tag.name}:{tag.tag_collection.name if tag.tag_collection else ''}" for tag in action.tags.all()]),
                "Community": action.community.name if action.community else "",
            })
            data.append(cell)
        return data


    def _export_all_testimonials(self):
        testimonials = Testimonial.objects.filter(is_deleted=False,is_published=True)
        columns = ["Title", "Body", "User", "Related Action", "Related Vendor", "Image", "Tags", "Email", "Community"]
        data = [columns]
        
        for testimonial in testimonials:
            cell = self._get_cells_from_dict(columns, {
                "Title": testimonial.title,
                "Body": testimonial.body,
                "User": testimonial.user.full_name if testimonial.user else testimonial.preferred_name or "",
                "Related Action": testimonial.action.title if testimonial.action else "",
                "Related Vendor": testimonial.vendor.name if testimonial.vendor else "",
                "Image": testimonial.image.file.url if testimonial.image else "",
                "Tags": ", ".join([f"{tag.name}:{tag.tag_collection.name if tag.tag_collection else ''}" for tag in testimonial.tags.all()]),
                "Email": testimonial.user.email if testimonial.user else "",
                "Community": testimonial.community.name if testimonial.community else "",
            })
            data.append(cell)
        return data
    
    def _export_all_events(self):
        events = Event.objects.filter(is_deleted=False,is_published=True)
        columns = ["Title", "Description", "Start Date", "End Date", "Location", "Event Type", "Link", "Image", "Tags", "Community"]
        data = [columns]
        
        for event in events:
            local_start = get_massachusetts_time(event.start_date_and_time) if event.start_date_and_time else ""
            local_end = get_massachusetts_time(event.end_date_and_time) if event.end_date_and_time else ""
            cell = self._get_cells_from_dict(columns, {
                "Title": event.name,
                "Description": event.description,
                "Start Date": local_start.strftime("%Y-%m-%d %H:%M") if event.start_date_and_time else "",
                "End Date": local_end.strftime("%Y-%m-%d %H:%M") if event.end_date_and_time else "",
                "Location": event.location,
                "Event Type": event.event_type,
                "Link": event.external_link if event.external_link else "",
                "Image": event.image.file.url if event.image else "",
                "Tags": ", ".join([f"{tag.name}:{tag.tag_collection.name if tag.tag_collection else ''}" for tag in event.tags.all()]),
                "Community": event.community.name if event.community else "",
            })
            data.append(cell)
        return data
    

    def _export_all_events_for_wp(self, community_id=None):
        events = Event.objects.filter(is_deleted=False,is_published=True)
        if community_id:
            events = events.filter(community__id=community_id)
        columns = [
            "EVENT NAME", "EVENT EXCERPT", "EVENT VENUE NAME", "EVENT ORGANIZER NAME", 
            "EVENT START DATE", "EVENT START TIME", "EVENT END DATE", "EVENT END TIME", 
            "ALL DAY EVENT", "TIMEZONE", "HIDE FROM EVENT LISTINGS", "STICKY IN MONTH VIEW", 
            "EVENT CATEGORY", "EVENT TAGS", "EVENT COST", "EVENT CURRENCY SYMBOL", 
            "EVENT CURRENCY POSITION", "EVENT ISO CURRENCY CODE", "EVENT FEATURED IMAGE", 
            "EVENT WEBSITE", "EVENT SHOW MAP LINK", "EVENT SHOW MAP", "ALLOW COMMENTS", 
            "ALLOW TRACKBACKS AND PINGBACKS", "EVENT DESCRIPTION"
        ]
        data = [columns]
        
        for event in events:
            # Format dates and times - convert to Massachusetts timezone
            local_start = get_massachusetts_time(event.start_date_and_time) if event.start_date_and_time else None
            local_end = get_massachusetts_time(event.end_date_and_time) if event.end_date_and_time else None
            
            start_date = local_start.strftime("%Y-%m-%d") if local_start else ""
            start_time = local_start.strftime("%I:%M %p") if local_start else ""
            end_date = local_end.strftime("%Y-%m-%d") if local_end else ""
            end_time = local_end.strftime("%I:%M %p") if local_end else ""
            
            # Determine if it's an all-day event (if start and end are on same day and times are 00:00)
            is_all_day = False
            if event.start_date_and_time and event.end_date_and_time:
                if (event.start_date_and_time.date() == event.end_date_and_time.date() and
                    event.start_date_and_time.hour == 0 and event.start_date_and_time.minute == 0 and
                    event.end_date_and_time.hour == 0 and event.end_date_and_time.minute == 0):
                    is_all_day = True
            
            # Extract venue name from location JSON
            venue_name = ""
            if event.location and isinstance(event.location, dict):
                venue_name = event.location.get('name', '') or event.location.get('address', '')
            
            # Get organizer name
            organizer_name = ""
            if event.user:
                organizer_name = event.user.full_name or event.user.preferred_name or event.user.email
            
            # Get event type/category
            event_category = event.event_type or "Event"
            
            # Get tags
            tags = ", ".join([f"{tag.name}:{tag.tag_collection.name if tag.tag_collection else ''}" for tag in event.tags.all()])
            
            # Get featured image URL
            featured_image = ""
            if event.image and event.image.file:
                featured_image = event.image.file.url
            
            # Get external link as website
            website = event.external_link or ""
            
            cell = self._get_cells_from_dict(columns, {
                "EVENT NAME": event.name,
                "EVENT EXCERPT": event.featured_summary or "",
                "EVENT VENUE NAME": venue_name,
                "EVENT ORGANIZER NAME": organizer_name,
                "EVENT START DATE": start_date,
                "EVENT START TIME": start_time,
                "EVENT END DATE": end_date,
                "EVENT END TIME": end_time,
                "ALL DAY EVENT": "TRUE" if is_all_day else "FALSE",
                "TIMEZONE": "America/New_York",  # Default timezone
                "HIDE FROM EVENT LISTINGS": "FALSE",
                "STICKY IN MONTH VIEW": "FALSE",
                "EVENT CATEGORY": event_category,
                "EVENT TAGS": tags,
                "EVENT COST": "",  # No cost field in Event model
                "EVENT CURRENCY SYMBOL": "",
                "EVENT CURRENCY POSITION": "",
                "EVENT ISO CURRENCY CODE": "",
                "EVENT FEATURED IMAGE": featured_image,
                "EVENT WEBSITE": website,
                "EVENT SHOW MAP LINK": "TRUE" if venue_name else "FALSE",
                "EVENT SHOW MAP": "TRUE" if venue_name else "FALSE",
                "ALLOW COMMENTS": "FALSE",
                "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
                "EVENT DESCRIPTION": event.description
            })
            data.append(cell)
        return data
    
    def _build_quick_links_json(self, community_id):
        from datetime import datetime
        
        home_page = HomePageSettings.objects.filter(community__id=community_id).first()
        
        # No home page or no featured links
        if not home_page or not home_page.featured_links:
            return json.dumps({"featured_links": []})

        # featured_links may be stored as JSON string or list
        links = home_page.featured_links
        try:
            if isinstance(links, str):
                links = json.loads(links)
        except Exception:
            # If parsing fails, return empty array
            return json.dumps({"featured_links": []})

        # Clean the links to ensure JSON serializable
        clean_links = self._clean_datetime_for_json(links or [])
        
        data = {"featured_links": clean_links}
        return json.dumps(data, indent=2)
    

    
    def _build_home_page_json(self, community_id):
        from database.utils.common import get_images_in_sequence
        from datetime import datetime
        
        home_page = HomePageSettings.objects.filter(community__id=community_id).first()
        if not home_page:
            return json.dumps({
                "title": "",
                "images": []
            })
        
        title = home_page.sub_title or ""
        images = home_page.images.all()
        sequence = home_page.image_sequence.sequence if home_page.image_sequence else None
        image_list = (
            get_images_in_sequence(images, json.loads(sequence))
            if sequence
            else [i.simple_json() for i in images]
        )

        # Clean the image list to ensure JSON serializable
        clean_image_list = self._clean_datetime_for_json(image_list)

        data = {
            "title": title,
            "images": clean_image_list
        }
        
        return json.dumps(data, indent=2)

    def _build_about_us_json(self, community_id):
        from datetime import datetime
        
        about_us = AboutUsPageSettings.objects.filter(community__id=community_id).first()
        
        if not about_us:
            return json.dumps({
                "description": "",
                "featured_video": "",
                "title": "",
                "subtitle": ""
            })

        data = {
            "description": about_us.description or "",
            "featured_video": about_us.featured_video_link or "",
            "title": about_us.title or "",
            "subtitle": about_us.sub_title or ""
        }
        
        # Clean any datetime objects in the data
        clean_data = self._clean_datetime_for_json(data)
        return json.dumps(clean_data, indent=2)

    def upload_zip_to_s3(self, file_buffer, filename):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name= os.environ.get('AWS_S3_REGION_NAME'),
        )

        s3.upload_fileobj(
            file_buffer,
            os.environ.get('AWS_STORAGE_BUCKET_NAME'),
            filename,
            ExtraArgs={"ContentType": "application/zip"}
        )

    def generate_presigned_url(self, filename, expires_in=3600):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME'),
        )

        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": os.environ.get('AWS_STORAGE_BUCKET_NAME'), "Key": filename},
            ExpiresIn=expires_in,
        )
    
    def _build_contact_json(self, community_id):
        from datetime import datetime
        
        community = Community.objects.get(id=community_id)
        
        # Get location information
        community_location = community.locations.first()
        if community_location:
            # Build location string from available fields
            location_parts = []
            if community_location.city:
                location_parts.append(community_location.city)
            if community_location.state:
                location_parts.append(community_location.state)
            if community_location.zipcode:
                location_parts.append(community_location.zipcode)
            
            location = ", ".join(location_parts) if location_parts else ""
        else:
            # Fallback to community.location field if locations relationship is empty
            if community.location:
                try:
                    location_data = json.loads(community.location)
                    location_parts = []
                    if location_data.get("city"):
                        location_parts.append(location_data["city"])
                    if location_data.get("state"):
                        location_parts.append(location_data["state"])
                    if location_data.get("zipcode"):
                        location_parts.append(location_data["zipcode"])
                    
                    location = ", ".join(location_parts) if location_parts else ""
                except (json.JSONDecodeError, TypeError):
                    location = ""
            else:
                location = ""
        
        # Get media URLs
        logo_url = community.logo.file.url if community.logo else ""
        
        data = {
            "admin_name": community.owner_name or "",
            "admin_email": community.owner_email or "",
            "admin_phone_number": community.owner_phone_number or "",
            "logo": logo_url,
            "address_line_1": location,
        }
        
        # Clean any datetime objects in the data
        clean_data = self._clean_datetime_for_json(data)
        return json.dumps(clean_data, indent=2)

    def _build_socials_json(self, community_id):
        
        community = Community.objects.filter(id=community_id).first()
        if not community:
            return json.dumps({
                "facebook_url": "",
                "instagram_url": "",
                "twitter_url": ""
            })
        
        # Handle more_info safely
        more_info = {}
        if community.more_info:
            try:
                more_info = json.loads(community.more_info)
            except (json.JSONDecodeError, TypeError):
                more_info = {}
        
        facebook = more_info.get("facebook_link", "") or ""
        instagram_link = more_info.get("instagram_link", "") or ""
        twitter_link = more_info.get("twitter_link", "") or ""
        
        data = {
           "facebook_url": facebook,
           "instagram_url": instagram_link,
           "twitter_url": twitter_link,
        }
        
        # Clean any datetime objects in the data
        clean_data = self._clean_datetime_for_json(data)
        return json.dumps(clean_data, indent=2)

    

    def export_site_data(self, context: Context, community_id=None):
        community = Community.objects.get(id=community_id)
        files = {
            "actions.csv": self._export_community_actions(community_id),
            "events.csv": self._community_events_download(community_id),
            "testimonials.csv": self._community_testimonials_download(community_id),
            "vendors.csv": self._community_vendors_download(community_id),
            "home_page.json": self._build_home_page_json(community_id),
            "featured_links.json": self._build_quick_links_json(community_id),
            "about_us.json": self._build_about_us_json(community_id),
            "contact.json":self._build_contact_json(community_id),
            "socials.json":self._build_socials_json(community_id)
        }
        zip_file = self._create_zip(files)
        filename = f"{community.name}-site-data.zip"
        self.upload_zip_to_s3(zip_file, filename)
        download_link = self.generate_presigned_url(filename)
        return (download_link, community.name), None



    def _create_zip(self, files):
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, content in files.items():
                    if content is None:
                        continue
                    if isinstance(content, str):
                        zf.writestr(name, content)
                    elif isinstance(content, list):
                        # Convert list data to CSV format
                        csv_buffer = io.StringIO()
                        writer = csv.writer(csv_buffer)
                        for row in content:
                            writer.writerow(row)
                        zf.writestr(name, csv_buffer.getvalue())
                    else:
                        zf.writestr(name, content.getvalue() if hasattr(content, "getvalue") else content)
            buffer.seek(0)
            return buffer