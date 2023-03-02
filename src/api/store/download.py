from _main_.utils.massenergize_errors import (
    NotAuthorizedError,
    MassEnergizeAPIError,
    InvalidResourceError,
    CustomMassenergizeError,
)
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
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
)
from api.store.team import get_team_users
from api.utils.constants import STANDARD_USER, GUEST_USER
from api.store.tag_collection import TagCollectionStore
from api.store.deviceprofile import DeviceStore
from django.db.models import Q
from sentry_sdk import capture_message
from typing import Tuple

from django.utils import timezone
import datetime
from django.utils.timezone import utc

EMPTY_DOWNLOAD = (None, None)


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


        # Fields should include for Actions, Households, Carbon Reduction: user reported, manual addition, goal for this period, (calculated) % of goal.

        # For Actions entered data - the numbers entered into each category.

        self.community_id = None

        self.metrics_columns = ["anonymous_users", "user_profiles"]
        # self.metrics_columns = ['anonymous_users', 'user_profiles', 'profiles_over_time'] # TODO: Use after profiles over time is working

    def _get_cells_from_dict(self, columns, data):
        cells = ["" for _ in range(len(columns))]

        for key, value in data.items():
            if type(value) == int or type(value) == float:
                value = str(value)
            if not value:
                continue

            cells[columns.index(key)] = value
        return cells

    #Given user, returns first part of populated row for Users CSV
    def _get_user_info_cells_1(self, user):
        user_cells_1 = {}

        if isinstance(user, Subscriber):
            full_name = user.name
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
            user_households = user.real_estate_units.count()


            sign_in_date = user.visit_log[-1] if len(user.visit_log) >=1 else user.updated_at.strftime("%Y/%m/%d") if user.updated_at else placeholder

            user_cells_2 = {
                "Households (count)": user_households,
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
    
    # Recieves an action, returns how many times it's been marked as Done in the last 30 days
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
            action.calculator_action.average_points
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
            rows.append(
                self._get_cells_from_dict(
                    self.action_info_columns,
                    {
                        "Action": "STATE-REPORTED",
                        "Done (count)": str(data.reported_value),
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
                        done_action.action.calculator_action.average_points
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


    #Gets row information for each community for All Communities CSV
    def _get_community_info_cells(self, community):
        
        location_string = self.get_location_string(community)

        community_members, teams_count, events_count, actions_count, testimonials_count, actions = self.community_info_helper(community)
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
                action_rel.action.calculator_action.average_points
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
        users = list(
            UserProfile.objects.filter(
                is_deleted=False, 
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
    def _all_actions_download(self):
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
                community = ""
            data.append([community] + [is_focused] + self._get_action_info_cells(action))

        #get state reported actions
        communities = Community.objects.filter(is_deleted=False)
        for com in communities:
            community_reported_rows = self._get_reported_data_rows(com)
            for row in community_reported_rows:
                data.append([com.name]+ row)

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

        for community in communities:
            data.append(self._get_community_info_cells(community))

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

    # Unused currently, for Metrics CSV
    def _community_metrics_download(self, context, args, community_id):
        community = Community.objects.filter(id=community_id)
        columns = self.metrics_columns
        data = [columns]
        device_store = DeviceStore()

        anonymous_users, err = device_store.metric_anonymous_community_users(
            community_id
        )
        user_profiles, err = device_store.metric_community_profiles(community_id)
        data.append([anonymous_users, user_profiles])
        # profiles_over_time, err = DeviceStore.metric_community_profiles_over_time(context, args, community_id)
        # TODO: Coming back to this ^^^ after downloads is done

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
                    return (
                        self._community_users_download(community_id),
                        community_name,
                    ), None
                else:
                    #All Users CSV method for all users overall
                    return (self._all_users_download(), None), None
            elif context.user_is_community_admin:
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
            capture_message(str(e), level="error")
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
    
    #For All Actions CSV and (for superadmins) the All Communities and Actions CSV
    def actions_download(
        self, context: Context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            self.community_id = community_id
            if community_id:
                community_name = Community.objects.get(id=community_id).name
                return (
                    #All Actions CSV method - action data for one community
                    self._community_actions_download(community_id),
                    community_name,
                ), None
            elif context.user_is_super_admin:
                #All Communities and Actions CSV method - action data across all communities
                return (self._all_actions_download(), None), None
        except Exception as e:
            capture_message(str(e), level="error")
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
            capture_message(str(e), level="error")
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

    #For Teams CSV --  information about the Teams in a given community
    def teams_download(
        self, context: Context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        self.community_id = community_id
        try:
            if context.user_is_community_admin or context.user_is_super_admin:
                community = Community.objects.get(id=community_id)
                if community:
                    return (
                        self._community_teams_download(community.id),
                        community.name,
                    ), None
                else:
                    return EMPTY_DOWNLOAD, InvalidResourceError()
            else:
                return EMPTY_DOWNLOAD, NotAuthorizedError()
        except Exception as e:
            capture_message(str(e), level="error")
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

    #Unused currently, for Metrics CSV
    def metrics_download(
        self, context: Context, args, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if not context.user_is_admin():
                return EMPTY_DOWNLOAD, NotAuthorizedError()
            return (
                self._community_metrics_download(context, args, community_id),
                None,
            ), None
        except Exception as e:
            capture_message(str(e), level="error")
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)
