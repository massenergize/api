"""
This File contains tasks used to fix missing or incorrect data in certain database models.
These were formerly in a 'data.backfill' route in misc.py.  
Some are obsolete and not relevant any longer, but kept for posterity in case needed.

1. backfill_subdomains: loop over communities, created Subdomain instances for each
2. backfill_teams: loop through Teams, create TeamMember instances
3. backfill_community_memebers: loop through UserProfile and CommunityAdminGroups to create CommunityJembers
4. backfill_graph_default_data: fix action done category data
5. backfill_locations: add more complete address fields to RealEstateUnits and Communities
"""
import csv
import datetime
from _main_.utils.massenergize_logger import log
import zipcodes
from django.http import HttpResponse
from database.models import (
    Subdomain,
    Community,
    Team,
    TeamMember,
    CommunityMember,
    RealEstateUnit,
    CommunityAdminGroup,
    UserProfile,
    Data,
    TagCollection,
    UserActionRel,
    Location,
)
from database.utils.common import json_loader
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.store.utils import find_reu_community, split_location_string, check_location
from api.utils.constants import DATA_DOWNLOAD_TEMPLATE


def write_to_csv(data):
    response = HttpResponse(content_type="text/csv")
    writer = csv.DictWriter(response, fieldnames=["Message", "Error"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return response.content


def backfill_data(task=None):
    try:
        #data = backfill_subdomains()
        #data = backfill_teams()
        #data = backfill_community_members()
        #data = backfill_graph_default_data()
        data = backfill_locations()
        if len(data) > 0:
            report =  write_to_csv(data)
            temp_data = {'data_type': "Content Spacing", "name":task.creator.full_name if task.creator else "admin"}
            file_name = "Data-Backfill-Report-{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%d"))
            send_massenergize_email_with_attachments(DATA_DOWNLOAD_TEMPLATE,temp_data,[task.creator.email], report, file_name)
        return True
    
    except Exception as e:
        log.exception(e)
        return False


def backfill_subdomans():
    data = []
    for c in Community.objects.all():
        try:
            data.append({"Message": "Creating "+c.subdomain, "Error":""})
            Subdomain(name=c.subdomain, in_use=True, community=c).save()
        except Exception as e:
            data.append({"Message": "Error", "Error": str(e)})
    return data


def backfill_teams():
    data = []
    try:
        teams = Team.objects.all()
        for team in teams:
            members = team.members.all()
            for member in members:
                team_member = TeamMember.objects.filter(
                    user=member, team=team
                ).first()
                if team_member:
                    team_member.is_admin = False
                    team_member.save()
                if not team_member:
                    team_member = TeamMember.objects.create(
                        user=member, team=team, is_admin=False
                    )
            admins = team.admins.all()
            for admin in admins:
                team_member = TeamMember.objects.filter(
                    user=admin, team=team
                ).first()
                if team_member:
                    team_member.is_admin = True
                    team_member.save()
                else:
                    team_member = TeamMember.objects.create(
                        user=admin, team=team, is_admin=True
                    )
        return data
    
    except Exception as e:
        log.exception(e)
        data.append({"Message": "Fatal error", "Error": str(e)})
        return data

def backfill_community_members():
    data = []
    try:
        users = UserProfile.objects.filter(is_deleted=False)
        for user in users:
            for community in user.communities.all():
                community_member: CommunityMember = CommunityMember.objects.filter(
                    community=community, user=user
                ).first()
                if community_member:
                    community_member.is_admin = False
                    community_member.save()
                else:
                    community_member = CommunityMember.objects.create(
                        community=community, user=user, is_admin=False
                    )
        admin_groups = CommunityAdminGroup.objects.all()
        for group in admin_groups:
            for member in group.members.all():
                community_member: CommunityMember = CommunityMember.objects.filter(
                    community=group.community, user=member
                ).first()
                if community_member:
                    community_member.is_admin = True
                    community_member.save()
                else:
                    community_member = CommunityMember.objects.create(
                        community=group.community, user=member, is_admin=True
                    )
        return data
    except Exception as e:
        log.exception(e)
        data.append({"Message": "Fatal error", "Error": str(e)})
        return data


def backfill_graph_default_data():
    data = []
    try:
        for community in Community.objects.all():
            for tag in TagCollection.objects.get(
                name__icontains="Category"
            ).tag_set.all():
                d = Data.objects.filter(community=community, name=tag.name).first()
                if d:
                    oldval = d.value
                    val = 0
                    if community.is_geographically_focused:
                        user_actions = UserActionRel.objects.filter(
                            real_estate_unit__community=community, status="DONE"
                        )
                    else:
                        user_actions = UserActionRel.objects.filter(
                            action__community=community, status="DONE"
                        )
                    for user_action in user_actions:
                        if (
                            user_action.action
                            and user_action.action.tags.filter(pk=tag.id).exists()
                        ):
                            val += 1
                    d.value = val
                    d.save()
                    message = "Community: %s, Category: %s, Old: %s, New: %x" % (
                        community.name, tag.name, str(oldval), str(val))                    
                    data.append({"Message": message, "Error":""})

        return data
    except Exception as e:
        log.exception(e)
        data.append({"Message": "Fatal error", "Error": str(e)})
        return data


def backfill_locations():
    CHOICES = json_loader("./database/raw_data/other/databaseFieldChoices.json")
    location_types = CHOICES.get("LOCATION_TYPES")

    data = []
    # these were some bad addresses, already fixed
    # ZIPCODE_FIXES = json_loader("api/store/ZIPCODE_FIXES.json")
    try:
        # Update Community locations to be not just a zip code
        data.append({"Message": "Updating community locations", "Error":""})
        communities = Community.objects.filter(is_deleted=False)
        for community in communities:
            # a community can have multiple locations (for example zip codes)
            for location in community.locations.all():
                location_type = location.location_type
                msg = "Community: %s, location type: %s" % (community.name, location_type)
                data.append({"Message": msg, "Error":""})
                if location_type == "ZIP_CODE_ONLY":
                    # usual case
                    if location.zipcode and location.zipcode.isnumeric():
                        loc_data = zipcodes.matching(location.zipcode)[0]
                    else:
                        # training community - a problem
                        loc_data = zipcodes.filter_by(city=location.city, state=location.state)
                        if not loc_data:
                            data.append({"Message": "Skipping", "Error":"Incomplete location"})
                            continue
                        loc_data = loc_data[0]

                    data.append({"Message": "Updating to FULL_ADDRESS", "Error":""})
                    location.city = loc_data["city"]
                    location.county = loc_data["county"]
                    location.state = loc_data["state"]
                    location.country = loc_data["country"]
                    location.location_type = "FULL_ADDRESS"
                    location.save()

                elif location_type == "CITY_ONLY" and (not location.county or not location.country):
                    # add the county if missing
                    data.append({"Message": "Updating with county", "Error":""})
                    loc_data = zipcodes.filter_by(
                        city=location.city, state=location.state, zip_code_type="STANDARD"
                    )[0]
                    location.county = loc_data["county"]
                    location.country = loc_data["country"]
                    location.save()                    

        # BHN - Feb 2021 - assign all real estate units to geographic communities
        # Set the community of a real estate unit based on the location of the real estate unit.
        # This defines what geographic community, if any gets credit
        # For now, check for zip code
        data.append({"Message": "", "Error":""})
        data.append({"Message": "Updating real estate unit locations", "Error":""})
        reu_all = RealEstateUnit.objects.filter(is_deleted=False)
        msg = "Number of real estate units:" + str(reu_all.count())
        data.append({"Message": msg, "Error":""})

        userProfiles = UserProfile.objects.prefetch_related(
            "real_estate_units"
        ).filter(is_deleted=False)
        msg = "number of user profiles:" + str(userProfiles.count())
        data.append({"Message": msg, "Error":""})

        # loop over profiles and realEstateUnits associated with them
        for userProfile in userProfiles:
            reus = userProfile.real_estate_units.all()
            msg = "User: %s (%s), %d households - %s" % (
                userProfile.full_name,
                userProfile.email,
                reus.count(),
                userProfile.created_at.strftime("%Y-%m-%d"),
            )
            data.append({"Message": msg, "Error":""})

            for reu in reus:
                street = unit_number = city = county = state = zip = ""
                loc = reu.location  # a JSON field
                zip = None
                if loc:
                    # if not isinstance(loc,str):
                    #  # one odd case in dev DB, looked like a Dict
                    #  print("REU location not a string: "+str(loc)+" Type="+str(type(loc)))
                    #  loc = loc["street"]
                    loc_parts = split_location_string(loc)
                    if len(loc_parts) >= 4:
                        # deal with odd cases
                        street = loc_parts[0].capitalize()
                        city = loc_parts[1].capitalize()
                        state = loc_parts[2].upper()
                        zip = loc_parts[3].strip()
                        if not zip or (len(zip) != 5 and len(zip) != 10):
                            msg =   "Invalid zipcode: " + zip + ", setting to 00000"
                            data.append({"Message": "Warning", "Error":msg})
                            zip = "00000"
                        elif len(zip) == 10:
                            zip = zip[0:5]
                    else:
                        # deal with odd cases which were encountered in the dev database
                        zip = "00000"
                        state = "MA"  # may be wrong occasionally
                        msg = "Zipcode assigned " + zip
                        data.append({"Message": msg, "Error":""})

                    # create the Location for the RealEstateUnit
                    try:
                        if zipcodes.is_real(zip):
                            info = zipcodes.matching(zip)[0]
                            city = info["city"]
                            state = info["state"]
                            county = info["county"]
                            country = info["country"]
                        location_type, valid = check_location(
                            street, unit_number, city, state, zip
                        )
                        if not valid:
                            msg = "check_location returns: " + location_type
                            data.append({"Message": "Warning", "Error":msg})
                            continue
                        
                        msg = "Updating location for REU ID ", str(reu.id)
                        data.append({"Message": msg, "Error":""})
            
                        newloc, created = Location.objects.get_or_create(
                            location_type=location_type,
                            street=street,
                            unit_number=unit_number,
                            zipcode=zip,
                            city=city,
                            county=county,
                            state=state,
                        )
                        if created:
                            msg = "Zipcode " + zip + " created for town " + city
                        else:
                            msg = "Zipcode " + zip + " found for town " + city
                        data.append({"Message": msg, "Error":""})
                        reu.address = newloc
                        reu.save()

                        community = find_reu_community(reu)
                        if community:
                            msg = "Adding the REU with zipcode "+ zip+ " to the community "+ community.name
                            data.append({"Message": msg, "Error":""})          
                            reu.community = community
                        elif reu.community:
                            msg = "REU not located in any community, but was labeled as belonging to the community "+ reu.community.name
                            data.append({"Message": msg, "Error":""})          
                            reu.community = None
                        reu.save()
                    except Exception as e:
                        data.append({"Message": "Error", "Error": str(e)})
        return data
    
    except Exception as e:
        log.exception(e)
        data.append({"Message": "Fatal error", "Error": str(e)})
        return data
