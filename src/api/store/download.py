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


        self.action_info_columns_new = [
            "Action", #rename from title
            "Done in last 30 days (count)", #new 
            "Done (count)", #rename
            "Annual GHG reduced per action (lbs)", #renamed from yearly_lbs_carbon
            "Total annual GHG reduced (lbs)", #renamed from total_yearly_lbs_carbon
            "To-do (count)", #new
            "Testimonials (count)", #rename
            "Impact",
            "Cost", #renamed
            "Category", #renamed
            "Carbon Calculator Action", #renamed
            "Live", #NEW 
            # "Geographically", # NEW
        ]

        self.user_info_columns_1 = [
            "First Name",
            "Last Name",
            "Preferred Name", 
            "Email", 
        ]

        self.user_info_columns_2 = [
            "Role",
            "Created",
            "Last sign in", #to be implemented
        ]

        self.user_info_columns_new_a = [
            "Done (count)",
            "To-do (count)",
            "Testimonials (count)",
            "Teams (count)",
            "Teams",
        ]

        self.team_info_columns_new = [
            "Team Name", #from name
            "Members (count)", 
            "Actions done (count)",
            "To-do (count)",
            "Trending action(s)",
            "Testimonials (count)",
            "Total annual GHG reduced (lbs)", #total_yearly_lbs_carbon
            "Parent team",
        ]

        self.community_info_columns = [
            "name",
            "location",
            "members_count",
            "teams_count",
            "testimonials_count",
            "actions_count",
            "events_count",
            "actions_user_reported",
            "actions_manual_addition",
            "actions_state/partner_reported",
            "actions_total",
            "actions_goal",
            "actions_goal_fraction",
            "households_user_reported",
            "households_manual_addition",
            "households_state/partner_reported",
            "households_total",
            "households_goal",
            "households_goal_fraction",
            "carbon_user_reported",
            "carbon_manual_addition",
            "carbon_state/partner_reported",
            "carbon_total",
            "carbon_goal",
            "carbon_goal_fraction",
            "actions_per_member",
            "most_done_action",
            "second_most_done_action",
            "highest_impact_action",
            "second_highest_impact_action",
        ]
        for category in self.action_categories:
            self.community_info_columns += [
                category.name + " reported",
                category.name + " state/partner_reported",
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

            #RIGHT NOW updated_at values use dashes while visit_log values use slashes to understand
            #frequency of either
            sign_in_date = user.visit_log[-1] if len(user.visit_log) >=1 else user.updated_at.strftime("%Y-%m-%d") if user.updated_at else placeholder

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

            #RIGHT NOW updated_at values use dashes while visit_log values use slashes to understand
            #frequency of either
            sign_in_date = user.visit_log[-1] if len(user.visit_log) >=1 else user.updated_at.strftime("%Y-%m-%d") if user.updated_at else placeholder

            user_cells_2 = {
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


    #new helper method
    def _get_team_info_for_user(self, user, teams):
        teams_for_user = teams.filter(teammember__user=user).values_list(
                "name", "teammember__is_admin"
            )
        tfu = []
        for team_name, is_admin in teams_for_user:
            tfu.append((team_name + "(ADMIN)") if is_admin else team_name)
        return teams_for_user.count(), tfu

    #new helper method
    def _get_action_info_for_user(self, user):
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
        

    '''
    Makes Done (count), To-do (count), Testimonials (count), Teams (count), Teams columns 
    '''
    def _get_user_actions_cells_new(self, user, actions, teams):
        user_cells = {}

        if isinstance(user, Subscriber) or isinstance(user, RealEstateUnit):
            #confirm REU has no testimonials, actions or teams (even though linked to a User?)
            user_cells = {}

        else:
            user_testimonials = Testimonial.objects.filter(is_deleted=False, user=user)
            testimonials_count = user_testimonials.count() if user_testimonials else "0"

            todo_count, done_count = self._get_action_info_for_user(user)

            team_count, users_teams = self._get_team_info_for_user(user, teams)

            user_cells = {
                "Done (count)":done_count,
                "To-do (count)":todo_count,
                "Testimonials (count)": testimonials_count,
                "Teams (count)": team_count,
                "Teams": ', '.join(users_teams),
            }
        return self._get_cells_from_dict(self.user_info_columns_new_a, user_cells)
    

    def _get_last_30_days_count(self, action):
        today = datetime.date.today()
        thirty_days_ago = today - timezone.timedelta(days = 30)

        done_actions_30_days = UserActionRel.objects.filter(
            is_deleted=False, action=action, status="DONE", date_completed__gte=thirty_days_ago,
        ) #.values_list( "action", "date_completed" )

        return done_actions_30_days.count()

    
    def _get_action_info_cells_new(self, action):

        average_carbon_points = (
            action.calculator_action.average_points
            if action.calculator_action
            else int(action.average_carbon_score)
            if action.average_carbon_score.isdigit()
            else 0
        )

        is_published = "Yes" if action.is_published else "No"
        #print(action.geographic_area if action.geographic_area else "NO GEO AREA")

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
        
        action_cells_new = {
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
            "Live": is_published,
            #"Geographically",
        }

        return self._get_cells_from_dict(self.action_info_columns_new, action_cells_new)

    
    def _get_reported_data_rows_new(self, community):
        rows = []
        for action_category in self.action_categories:
            data = Data.objects.filter(tag=action_category, community=community).first()
            if not data:
                continue
            rows.append(
                self._get_cells_from_dict(
                    self.action_info_columns_new,
                    {
                        "Action": "STATE-REPORTED",
                        "Category": action_category.name,
                        "Done (count)": str(data.reported_value),
                    },
                )
            )
        return rows


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


    def _get_team_info_cells_new(self, team):
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

        placeholder = "placeholder"
        team_cells = {
            "Team Name": team.name,
            "Members (count)": members_count,
            "Actions done (count)": done_actions_count,
            "To-do (count)": todo_actions_count,
            "Trending action(s)": ', '.join(trending_actions),
            "Testimonials (count)": testimonials_count,
            "Total annual GHG reduced (lbs)": total_carbon_points, #total_yearly_lbs_carbon
            "Parent team": team.parent.name if team.parent else "",
        }
        return self._get_cells_from_dict(self.team_info_columns_new, team_cells)


    def _get_community_reported_data(self, community):
        community = Community.objects.get(pk=community.id)
        if not community:
            return None
        ret = {}
        for action_category in self.action_categories:
            data = Data.objects.filter(tag=action_category, community=community).first()
            if not data:
                continue
            ret[action_category.name + " reported"] = data.value
            ret[action_category.name + " state/partner_reported"] = data.reported_value
        return ret

    def _get_community_info_cells(self, community):

        location_string = ""
        if community.is_geographically_focused:
            location_string += "["
            for loc in community.locations.all():
                if location_string != "[":
                    location_string += ","
                location_string += str(loc)
            location_string += "]"

        community_members = CommunityMember.objects.filter(
            is_deleted=False, community=community
        ).select_related("user")
        users = [cm.user for cm in community_members]
        members_count = community_members.count()
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

        action_done_count_map = {
            action.title: done_action_rels.filter(action=action).count()
            for action in actions
        }
        actions_by_done_count = sorted(
            action_done_count_map.items(), key=lambda item: item[1], reverse=True
        )

        most_done_action = (
            actions_by_done_count[0][0]
            if actions_of_members > 0
            and (len(actions_by_done_count) > 0 and actions_by_done_count[0][1] != 0)
            else ""
        )
        second_most_done_action = (
            actions_by_done_count[1][0]
            if actions_of_members > 0
            and (len(actions_by_done_count) > 1 and actions_by_done_count[1][1] != 0)
            else ""
        )

        actions_by_impact = actions.order_by("calculator_action__average_points")
        highest_impact_action = (
            actions_by_impact[0]
            if actions_of_members > 0 and len(actions_by_impact) > 0
            else ""
        )
        second_highest_impact_action = (
            actions_by_impact[1]
            if actions_of_members > 0 and len(actions_by_impact) > 1
            else ""
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

        community_cells = {
            "name": community.name,
            "location": location_string,
            "members_count": str(members_count),
            "teams_count": teams_count,
            "actions_count": str(actions_count),
            "testimonials_count": testimonials_count,
            "events_count": events_count,
            "actions_user_reported": actions_user_reported,
            "actions_manual_addition": actions_manual_addition,
            "actions_state/partner_reported": actions_partner,
            "actions_total": actions_total,
            "actions_goal": actions_goal,
            "actions_goal_fraction": actions_fraction,
            "households_user_reported": households_count,
            "households_manual_addition": households_manual_addition,
            "households_state/partner_reported": households_partner,
            "households_total": households_total,
            "households_goal": households_goal,
            "households_goal_fraction": households_fraction,
            "carbon_user_reported": carbon_user_reported,
            "carbon_manual_addition": carbon_manual_addition,
            "carbon_state/partner_reported": carbon_partner,
            "carbon_total": carbon_total,
            "carbon_goal": carbon_goal,
            "carbon_goal_fraction": carbon_fraction,
            "actions_per_member": actions_per_member,
            "most_done_action": most_done_action,
            "second_most_done_action": second_most_done_action,
            "highest_impact_action": highest_impact_action,
            "second_highest_impact_action": second_highest_impact_action,
        }
        reported_actions = self._get_community_reported_data(community)
        community_cells.update(reported_actions)

        return self._get_cells_from_dict(self.community_info_columns, community_cells)

    def _one_action_download(self, action_id):

        #get user info for action
        user_info_for_action = {
                user_action_rel.action.id: user_action_rel
                for user_action_rel in UserActionRel.objects.filter(
                    is_deleted=False, user=user #FIX
                ).select_related("action")
            }
    
    def _all_users_download_new(self):
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
            + self.user_info_columns_new_a 
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
                + self._get_user_actions_cells_new(user, actions, teams)
                + self._get_user_info_cells_2(user)
            )
            data.append(row)

        # sort by community
        data = sorted(data, key=lambda row: row[0])
        # insert the columns
        data.insert(0, columns)

        return data

    def _community_users_download_new(self, community_id):
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
            self.user_info_columns_1 + self.user_info_columns_new_a + self.user_info_columns_2
        )
        data = [columns]

        for user in users:
            row = (
                self._get_user_info_cells_1(user)
                + self._get_user_actions_cells_new(user, actions, teams)
                + self._get_user_info_cells_2(user)
            )
            data.append(row)

        for household in community_households:
            if self._get_user_info_cells_2(household) is None:
                row = None
            else: 
                row = (self._get_user_info_cells_1(household)
                + ["" for _ in range(len(self.user_info_columns_new_a))]
                + self._get_user_info_cells_2(household)
            )
            if row:
                data.append(row)

        return data

    # based off of a method described as "new 1/11/20 BHN - untested"
    def _team_users_download_new(self, team_id, community_id):

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
        
        #team = Team.objects.get(id=team_id)

        teams = Team.objects.filter(is_deleted=False)
        community_id = team.primary_community.id
        actions = Action.objects.filter(
            Q(community__id=community_id) | Q(is_global=True)
        ).filter(is_deleted=False)

        columns = (
            self.user_info_columns_1 + self.user_info_columns_new_a + self.user_info_columns_2
        )

        data = [columns]
        for user in users:
            row = (
                self._get_user_info_cells_1(user)
                + self._get_user_actions_cells_new(user, actions, teams)
                + self._get_user_info_cells_2(user)
            )
            data.append(row)

        return data

    def _all_actions_download_new(self):
        actions = (
            Action.objects.select_related("calculator_action", "community")
            .prefetch_related("tags")
            .filter(is_deleted=False)
        )

        columns = ["Community"] + self.action_info_columns_new + ["Is Global"]
        data = []

        for action in actions:
            if not action.is_global and action.community:
                community = action.community.name
            else:
                community = ""
            data.append([community] + self._get_action_info_cells_new(action) + ["True" if action.is_global else "False"])

        #get state reported actions
        communities = Community.objects.filter(is_deleted=False)
        for com in communities:
            community_reported_rows = self._get_reported_data_rows_new(com)
            for row in community_reported_rows:
                data.append([com.name]+ row) #add is_global information here, always False?

        data = sorted(data, key=lambda row: row[0])  # sort by community
        data.insert(0, columns)  # insert the column names

        return data

    def _community_actions_download_new(self, community_id):
        actions = (
            Action.objects.filter(Q(community__id=community_id) | Q(is_global=True))
            .select_related("calculator_action")
            .prefetch_related("tags")
            .filter(is_deleted=False)
        )

        columns = self.action_info_columns_new
        data = [columns]

        for action in actions:
            data.append(self._get_action_info_cells_new(action))

        community = Community.objects.filter(id=community_id).first()
        community_reported_rows = self._get_reported_data_rows_new(community)
        for row in community_reported_rows:
            data.append(row)

        return data

    def _all_communities_download(self):
        communities = Community.objects.filter(is_deleted=False)
        columns = self.community_info_columns
        data = [columns]

        for community in communities:
            data.append(self._get_community_info_cells(community))

        return data

    def _community_teams_download_new(self, community_id):
        teams = Team.objects.filter(communities__id=community_id, is_deleted=False)
        actions = Action.objects.filter(
            Q(community__id=community_id) | Q(is_global=True)
        ).filter(is_deleted=False)

        columns = self.team_info_columns_new
        data = [columns]

        for team in teams:
            data.append(
                self._get_team_info_cells_new(team)
            )

        return data

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
                    return (self._team_users_download_new(team_id, community_id), community_name), None 
                elif community_id:
                    return (
                        self._community_users_download_new(community_id),
                        community_name,
                    ), None
                else:
                    return (self._all_users_download_new(), None), None
            elif context.user_is_community_admin:
                if team_id:
                    return (self._team_users_download_new(team_id, community_id), community_name), None
                elif community_id:
                    return (
                        self._community_users_download_new(community_id),
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
    
    #NEW ONE -- for both "all actions" and "all communities and actions"
    def actions_download(
        self, context: Context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            self.community_id = community_id
            if community_id:
                community_name = Community.objects.get(id=community_id).name
                return (
                    #could rename to all_actions_download
                    self._community_actions_download_new(community_id),
                    community_name,
                ), None
            elif context.user_is_super_admin:
                #could rename to all_communities_and_actions_download
                return (self._all_actions_download_new(), None), None
            # until all (communities and) actions button is removed from community portal, this will give an error
        except Exception as e:
            capture_message(str(e), level="error")
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

    #single action addition, untested
    def single_action_download(
        self, context: Context, community_id, action_id #might not need community ID
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            self.community_id = community_id
            if community_id:
                #do something different if in a community?
                community_name = Community.objects.get(id=community_id).name
            else:
                #might want to return action name
                return (self._one_action_download(action_id), None), None
        except Exception as e:
            capture_message(str(e), level="error")
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

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

    #edited to use new method
    def teams_download(
        self, context: Context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        self.community_id = community_id
        try:
            if context.user_is_community_admin or context.user_is_super_admin:
                community = Community.objects.get(id=community_id)
                if community:
                    return (
                        self._community_teams_download_new(community.id),
                        community.name,
                    ), None
                else:
                    return EMPTY_DOWNLOAD, InvalidResourceError()
            else:
                return EMPTY_DOWNLOAD, NotAuthorizedError()
        except Exception as e:
            capture_message(str(e), level="error")
            return EMPTY_DOWNLOAD, CustomMassenergizeError(e)

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
