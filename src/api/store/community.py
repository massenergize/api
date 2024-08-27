import math
from datetime import datetime, timedelta, timezone
from typing import Tuple

import zipcodes
from django.db.models import Q
from _main_.utils.massenergize_logger import log
from _main_.settings import IS_PROD, SLACK_SUPER_ADMINS_WEBHOOK_URL
from _main_.utils.constants import PUBLIC_EMAIL_DOMAINS, RESERVED_SUBDOMAIN_LIST
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import add_sender_signature, update_sender_signature
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagConstants
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from _main_.utils.massenergize_errors import (CustomMassenergizeError, InvalidResourceError, MassEnergizeAPIError,
                                              NotAuthorizedError)
from _main_.utils.metrics import timed
from _main_.utils.utils import strip_website
from api.services.utils import send_slack_message
from api.store.common import count_action_completed_and_todos
from api.store.graph import GraphStore
from api.tests.common import RESET
from api.utils.api_utils import get_distance_between_coords, is_admin_of_community
from api.utils.filter_functions import get_communities_filter_params
from database.models import AboutUsPageSettings, Action, ActionsPageSettings, Community, CommunityAdminGroup, \
    CommunityMember, CommunityNotificationSetting, ContactUsPageSettings, CustomCommunityWebsiteDomain, \
    DonatePageSettings, EventsPageSettings, FeatureFlag, get_enabled_flags, Goal, Graph, HomePageSettings, \
    ImpactPageSettings, Location, \
    Media, Menu, RealEstateUnit, RegisterPageSettings, SigninPageSettings, Subdomain, TeamsPageSettings, \
    TestimonialsPageSettings, UserProfile, VendorsPageSettings
from database.utils.common import json_loader
from .utils import (get_community, get_community_or_die, get_new_title, get_user_from_context, is_reu_in_community)
from ..constants import COMMUNITY_NOTIFICATION_TYPES
from ..tasks import automatically_activate_nudge
from celery.result import AsyncResult

ALL = "all"

cadmin_locked_fields=["subdomain", "is_geographically_focused", "locations", "Is_approved", "is_demo"]

def remove_cadmin_locked_fields(args):
    return {key: value for key, value in args.items() if key not in cadmin_locked_fields}


def _clone_page_settings(pageSettings, title, community):
    """
    Clone page settings for a new community from a template
    """
    page = pageSettings.objects.filter(is_template=True).first()
    if not page:
        template_community = Community.objects.get(subdomain="template")
        page = pageSettings.objects.create(
            is_template=True, community=template_community
        )
        page.save()
        page.pk = None

    page.pk = None

    page.title = title
    page.community = community
    page.is_template = False
    page.save()

    return page


def check_community_membership(feature_flag, should_enable, community):
    """
			This function checks and modifies the community membership of a feature flag
			based on the current audience setting and the should_enable parameter.
			
			:param feature_flag: FeatureFlag object to be modified.
			:param should_enable: Boolean indicating whether the feature flag should be enabled or disabled for the community.
			:param community: Community object that represents the community to be added or removed.
	
			:return: None. The function works by modifying the feature_flag object in-place.
			:rtype: None.
			"""
    
    # If the audience setting is "everyone" and the flag should not be enabled,
    # set the audience to "all_except" and add the community to the exception list.
    if feature_flag.audience == FeatureFlagConstants.for_everyone():
        if not should_enable:
            feature_flag.audience = FeatureFlagConstants.for_all_except()
            feature_flag.communities.add(community)
            feature_flag.save()
    
    # If the audience setting is "specific", and the flag should be enabled,
    # add the community to the list. If not, remove it from the list.
    elif feature_flag.audience == FeatureFlagConstants.for_specific_audience():
        if should_enable:
            feature_flag.communities.add(community)
        else:
            feature_flag.communities.remove(community)
        feature_flag.save()
    
    # If the audience setting is "all_except", and the flag should be enabled,
    # remove the community from the exception list. If not, add it to the list.
    elif feature_flag.audience == FeatureFlagConstants.for_all_except():
        if should_enable:
            feature_flag.communities.remove(community)
        else:
            feature_flag.communities.add(community)
        feature_flag.save()
        
        
def create_default_menu(community):
    if not community: return None
#     load the default menu json
    default_menu_json = json_loader("database/raw_data/portal/menu.json")
    menu = Menu(
        community=community,
        name="{} - Default Menu".format(community.subdomain),
        is_custom=True,
        is_published=True,
        content=default_menu_json.get("PortalMainNavLinks", []),
        footer_content=default_menu_json.get("PortalFooterLinks", {}),
        contact_info=default_menu_json.get("PortalFooterContactInfo", {}),
    )
    menu.save()
    


class CommunityStore:
    def __init__(self):
        self.name = "Community Store/DB"
        self.graph_store = GraphStore()

    def _check_geography_unique(self, community, geography_type, loc):
        """
        Ensure that the location 'loc' is not part of another geographic community
        """
        check_communities = Community.objects.filter(
            is_geographically_focused=True,
            geography_type=geography_type,
            is_deleted=False,
        ).prefetch_related("locations")
        for check_community in check_communities:
            if check_community.id == community.id:
                continue
            for location in check_community.locations.all():
                if geography_type == "ZIPCODE" and location.zipcode == loc:
                    # zip code already used
                    message = (
                        "Zipcode %s is already part of another geographic community %s."
                        % (loc, check_community.name)
                    )
                    print(message)
                    raise Exception(message)
                elif geography_type == "CITY" and location.city == loc:
                    message = (
                        "City %s is already part of another geographic community %s."
                        % (loc, check_community.name)
                    )
                    print(message)
                    raise Exception(message)
                elif geography_type == "COUNTY" and location.county == loc:
                    message = (
                        "County %s is already part of another geographic community %s."
                        % (loc, check_community.name)
                    )
                    print(message)
                    raise Exception(message)
                elif geography_type == "STATE" and location.state == loc:
                    message = (
                        "State (%s) is already part of another geographic community (%s)."
                        % (loc, check_community.name)
                    )
                    print(message)
                    raise Exception(message)
                elif geography_type == "COUNTRY" and location.country == loc:
                    message = (
                        "Country (%s) is already part of another geographic community (%s)."
                        % (loc, check_community.name)
                    )
                    print(message)
                    raise Exception(message)

    def _are_locations_updated(self, geography_type, locations, community):
        """
        Check the locations for an updated geographic community to see if they are changed
        """
        if not community.locations:
            return True

        # this is a list of zipcodes, towns, cities, counties, states
        location_list = locations.replace(", ", ",").split(
            ","
        )  # passed as comma separated list
        if len(location_list) == community.locations.all().count():
            for loc in community.locations.all():
                if geography_type == "ZIPCODE" and not loc.zipcode in location_list:
                    return True
                elif geography_type == "CITY" and not loc.city in location_list:
                    return True
                elif geography_type == "COUNTY" and not loc.county in location_list:
                    return True
                elif geography_type == "STATE" and not loc.state in location_list:
                    return True
                elif geography_type == "COUNTRY" and not loc.country in location_list:
                    return True
        else:
            # different number, must have changed
            return True

        # Locations not updated
        return False

    def _update_locations(self, geography_type, locations, community):
        """
        Fill the locations for an updated geographic community
        """
        # clean up in case there is garbage in there
        if community.locations:
            community.locations.clear()

        # this is a list of zipcodes, towns, cities, counties, states
        location_list = locations.replace(", ", ",").split(
            ","
        )  # passed as comma separated list
        print("Community includes the following locations :" + str(location_list))
        for location in location_list:
            if geography_type == "ZIPCODE":
                if location[0].isdigit():
                    location = location.replace(" ", "")

                    # looks like a zipcode.  Check which towns it corresponds to
                    zipcode = zipcodes.matching(location)
                    if len(zipcode) > 0:
                        city = zipcode[0].get("city", None)
                        county  = zipcode[0].get("county", None)
                        state = zipcode[0].get("state", None)
                    else:
                        raise Exception("No zip code entry found for zip=" + location)

                    # get_or_create gives an error if multiple such locations exist (which can happen)
                    loc = Location.objects.filter(
                        location_type="FULL_ADDRESS", zipcode=location, city=city, county=county, state=state
                    )
                    if not loc:
                        loc = Location.objects.create(
                            location_type="FULL_ADDRESS", zipcode=location, city=city, county=county, state=state
                        )
                    else:
                        loc = loc.first()
                    self._check_geography_unique(community, geography_type, location)

                else:
                    # assume this is a town, see we can find the zip codes associated with it
                    ss = location.split("-")
                    town = ss[0]
                    if len(ss) == 2:
                        state = ss[1]
                    else:
                        state = "MA"

                    zips = zipcodes.filter_by(
                        city=town, state=state, zip_code_type="STANDARD"
                    )
                    if len(zips) > 0:
                        for zip in zips:
                            zipcode = zip.get("zip_code")
                            county = zip.get("county")

                            # get_or_create gives an error if multiple such locations exist (which can happen)
                            # loc, created = Location.objects.get_or_create(location_type='ZIP_CODE_ONLY', zipcode=location, city=city)
                            loc = Location.objects.filter(
                                location_type="FULL_ADDRESS", zipcode=zipcode, city=town, county=county, state=state
                            )
                            if not loc:
                                loc = Location.objects.create(
                                    location_type="FULL_ADDRESS", zipcode=location, city=city, county=county, state=state
                                )
                            else:
                                loc = loc.first()
                            self._check_geography_unique(community, geography_type, zipcode)

                    else:
                        msg = "No zipcodes found corresponding to town " + town + ", " + state    
                        raise Exception(msg)
                    
            elif geography_type == "CITY":
                # check that this city is found in the zipcodes list
                ss = location.split("-")
                city = ss[0]
                if len(ss) == 2:
                    state = ss[1]
                else:
                    state = "MA"

                zips = zipcodes.filter_by(
                    city=city, state=state, zip_code_type="STANDARD"
                )
                if len(zips) > 0:
                    # get_or_create gives an error if multiple such locations exist (which can happen)
                    county = zips[0].get("county")
                    loc = Location.objects.filter(
                        location_type="FULL_ADDRESS", zipcode=location, city=city, county=county, state=state
                    )
                    if not loc:
                        loc = Location.objects.create(
                            location_type="FULL_ADDRESS", zipcode=location, city=city, county=county, state=state
                        )
                    else:
                        loc = loc.first()
                else:
                    msg = "No zipcodes found corresponding to city " + city + ", " + state
                    raise Exception(msg)

                self._check_geography_unique(community, geography_type, city)
            elif geography_type == "COUNTY":
                # check that this county is found in the zipcodes list
                ss = location.split("-")
                county = ss[0]
                if len(ss) == 2:
                    state = ss[1]
                else:
                    state = "MA"

                zips = zipcodes.filter_by(
                    county=county, state=state, zip_code_type="STANDARD"
                )
                if len(zips) > 0:
                    # get_or_create gives an error if multiple such locations exist (which can happen)
                    loc = Location.objects.filter(
                        location_type="COUNTY_ONLY", county=county, state=state
                    )
                    if not loc:
                        loc = Location.objects.create(
                            location_type="COUNTY_ONLY", county=county, state=state
                        )
                    else:
                        loc = loc.first()

                else:
                    msg = "No zipcodes found corresponding to county " + county + ", " + state
                    raise Exception(msg)

                self._check_geography_unique(community, geography_type, county)

            elif geography_type == "STATE":
                # check that this state is found in the zipcodes list
                state = location
                zips = zipcodes.filter_by(state=state, zip_code_type="STANDARD")
                print("Number of zipcodes = " + str(len(zips)))
                if len(zips) > 0:
                    # get_or_create gives an error if multiple such locations exist (which can happen)
                    # loc, created = Location.objects.get_or_create(location_type='ZIP_CODE_ONLY', zipcode=location, city=city)
                    loc = Location.objects.filter(
                        location_type="STATE_ONLY", state=state
                    )
                    if not loc:
                        loc = Location.objects.create(
                            location_type="STATE_ONLY", state=state
                        )
                    else:
                        loc = loc.first()
                else:
                    msg = "No zipcodes found corresponding to state " + location
                    raise Exception(msg)

                self._check_geography_unique(community, geography_type, location)

            elif geography_type == "COUNTRY":
                # check that this state is found in the zipcodes list
                country = location
                zips = zipcodes.filter_by(country=country, zip_code_type="STANDARD")
                if len(zips) > 0:
                    # get_or_create gives an error if multiple such locations exist (which can happen)
                    # loc, created = Location.objects.get_or_create(location_type='ZIP_CODE_ONLY', zipcode=location, city=city)
                    loc = Location.objects.filter(
                        location_type="COUNTRY_ONLY", country=country
                    )
                    if not loc:
                        loc = Location.objects.create(
                            location_type="COUNTRY_ONLY", country=country
                        )
                    else:
                        loc = loc.first()
                else:
                    msg = "No zipcodes found corresponding to country " + location
                    raise Exception(msg)

                self._check_geography_unique(community, geography_type, location)

            else:
                raise Exception("Unexpected geography type: " + str(geography_type))
            # should be a five character string
            community.locations.add(loc)

    def _update_real_estate_units_with_community(self, community):
        """
        Utility function used when Community added or updated
        Find any real estate units in the database which are located in this community,
        and update the link to the community.
        """
        ZIPCODE_FIXES = json_loader("api/store/ZIPCODE_FIXES.json")
        userProfiles = UserProfile.objects.prefetch_related("real_estate_units").filter(
            is_deleted=False
        )
        reus = RealEstateUnit.objects.all().select_related("address")
        print("Updating " + str(reus.count()) + " RealEstateUnits")

        # loop over profiles and realEstateUnits associated with them
        for userProfile in userProfiles:

            for reu in userProfile.real_estate_units.all():
                if reu.address:
                    zip = reu.address.zipcode
                    if not isinstance(zip, str) or len(zip) != 5:
                        address_string = str(reu.address)
                        print(
                            "REU invalid zipcode: address = "
                            + address_string
                            + " User "
                            + userProfile.email
                        )

                        zip = "00000"
                        city = ""
                        for loc in ZIPCODE_FIXES:
                            # temporary fixing known address problems in the database
                            if address_string.find(loc) >= 0:
                                zip = ZIPCODE_FIXES[loc]["zipcode"]
                                city = ZIPCODE_FIXES[loc]["city"]
                                break

                        reu.address.zipcode = zip
                        reu.address.city = city
                        reu.address.save()

                    if is_reu_in_community(reu, community):
                        print(
                            "Adding the REU with zipcode "
                            + zip
                            + " to the community "
                            + community.name
                        )
                        reu.community = community
                        reu.save()

                    elif reu.community and reu.community.id == community.id:
                        # this could be the case if the community was made smaller
                        print(
                            "REU not located in this community, but was labeled as belonging to the community"
                        )
                        reu.community = None
                        reu.save()

    def _haversince_distance(self, lat1: int, lon1: int, lat2: int, lon2: int):
        """
        Calculate the great circle distance between two points.
        """
        # convert decimal degrees to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        earth_radius = 6371  # km

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # calculate the distance in kilometers
        distance = earth_radius * c
        # convert to miles
        distance = distance * 0.621371

        return distance

    @timed
    def get_community_info(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community = get_community_or_die(context, args)

            # context.is_prod now means the prod database site.
            # if (not community.is_published) and context.is_prod and (not context.is_admin_site):
            if (
                (not community.is_published)
                and (not context.is_sandbox)
                and (not context.is_admin_site)
            ):
                # if the community is not live and we are fetching info on the community
                # on prod, we should pretend the community does not exist.
                return None, InvalidResourceError()

            if community.goal:
                category_graph, err = self.graph_store.graph_actions_completed(
                    context, {"community_id": community.id}
                )
                if not err:
                    # this could be slow?
                    data = category_graph["data"]
                    category_totals = [datum["reported_value"] for datum in data]
                    solar_households = 0

                    for datum in data:
                        if datum.get("name", None) == "Solar":
                            solar_households = datum["reported_value"]
                            break

                    goal = community.goal
                    total = (
                        goal.attained_number_of_households
                        + goal.attained_number_of_actions
                        + goal.attained_carbon_footprint_reduction
                    )

                    # 1/16/22 change from max(category_totals) to solar_households
                    goal.attained_number_of_households = solar_households
                    goal.attained_number_of_actions = sum(category_totals)
                    goal.attained_carbon_footprint_reduction = 0

                    newtotal = (
                        goal.attained_number_of_households
                        + goal.attained_number_of_actions
                        + goal.attained_carbon_footprint_reduction
                    )
                    if newtotal != total:
                        goal.save()

            return community, None
        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def join_community(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community = get_community_or_die(context, args)

            # FIX: this routine also used for Admin portal when adnin added to community
            user_id = args.get("user_id", None)
            if (user_id):
                user = UserProfile.objects.filter(pk=user_id).first()
            else:
                user = get_user_from_context(context)
            if not user:
                return None, CustomMassenergizeError("User not found")
            
            user.communities.add(community)
            user.save()

            community_member: CommunityMember = CommunityMember.objects.filter(
                community=community, user=user
            ).first()
            if not community_member:
                community_member = CommunityMember.objects.create(community=community, user=user, is_admin=False)

            return user, None
        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def leave_community(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community = get_community_or_die(context, args)
            user = get_user_from_context(context)
            if not user:
                return None, CustomMassenergizeError("User not found")

            # Don't allow leaving a community that you are an admin of
            admin_group: CommunityAdminGroup = CommunityAdminGroup.objects.filter(community=community).first()
            is_admin = admin_group.members.filter(id=user.id).exists()
            if is_admin:
                return None, CustomMassenergizeError("You can't leave a community you are an admin of.  Please have yourself removed as an admin, or contact support@massenergize.org")

            user.communities.remove(community)
            user.save()

            community_member: CommunityMember = CommunityMember.objects.filter(
                community=community, user=user
            ).first()
            if not community_member or (not community_member.is_admin):
                community_member.delete()

            return user, None
        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def list_communities(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if context.is_sandbox:
                communities = (
                    Community.objects.filter(is_deleted=False, is_approved=True)
                    .exclude(subdomain="template")
                    .order_by("name")
                )
            else:
                communities = (
                    Community.objects.filter(
                        is_deleted=False, is_approved=True, is_published=True
                    )
                    .exclude(subdomain="template")
                    .order_by("name")
                )

            if not communities:
                return [], None

            # check for zipcode:
            if zipcode := args.get("zipcode", None):
                if zipcodes.is_real(zipcode):
                    # filter communities by coordinates
                    filtered_communities = []

                    # get coordinates of the zipcode
                    zipcode_info = zipcodes.matching(zipcode)
                    zipcode_lat = zipcode_info[0]["lat"]
                    zipcode_long = zipcode_info[0]["long"]

                    max_distance = args.get("max_distance", 25)

                    added_communities = []
                    for community in communities:
                        if community.is_geographically_focused:
                            for location in community.locations.all():
                                # skip locations that don't include zipcode (bogus data in dev)
                                if not location.zipcode:
                                    continue
                                community_zipcode_info = zipcodes.matching(
                                    location.zipcode
                                )
                                community_zipcode_lat = community_zipcode_info[0]["lat"]
                                community_zipcode_long = community_zipcode_info[0][
                                    "long"
                                ]

                                distance_between_zipcodes = get_distance_between_coords(
                                    float(zipcode_lat),
                                    float(zipcode_long),
                                    float(community_zipcode_lat),
                                    float(community_zipcode_long),
                                )

                                if distance_between_zipcodes <= max_distance:
                                    if community.id not in added_communities:
                                        community.location[
                                            "distance"
                                        ] = distance_between_zipcodes
                                        filtered_communities.append(community)
                                        added_communities.append(community.id)
                        else:
                            filtered_communities.append(community)
                    return filtered_communities, None
                else:
                    return [], CustomMassenergizeError("Invalid Zipcode")

            return communities, None
        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def create_community(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        community = None
        try:
            subdomain = args.get("subdomain")
            if not can_use_this_subdomain(subdomain):
                raise Exception(
                    "Subdomain is already reserved.  Please, choose a different subdomain"
                )

            logo = args.pop("logo", None)

            # custom website url can be included
            website = args.pop("website", None)

            # The set of locations (zipcodes, cities, counties, states), stored as Location models, are what determines a boundary for a geograpically focussed community
            # This will work for the large majority of cases, but there may be some where a zip code overlaps a town or state boundary
            # These we can deal with by having the Location include city and or state fields
            locations = args.pop("locations", None)
            contact_sender_alias = args.get("contact_sender_alias", None)

            favicon = args.pop("favicon", None)
            community = Community.objects.create(**args)
            community.save()
            geographic = args.get("is_geographically_focused", False)
            if geographic:
                geography_type = args.get("geography_type", None)
                self._update_locations(geography_type, locations, community)
                self._update_real_estate_units_with_community(community)

            if logo:
                cLogo = Media.objects.filter(id=logo).first()
                community.logo = cLogo
            if favicon:
                cFav = Media(
                    file=favicon, name=f"{args.get('name', '')} CommunityFavicon"
                )
                cFav.save()
                community.favicon = cFav

            # create a goal for this community
            community_goal = Goal.objects.create(name=f"{community.name}-Goal")
            community.goal = community_goal
            community.save()
            # do this before all the cloning in case of failure
            reserve_subdomain(subdomain, community)

            # save custom website if specified
            if website:
                ret, err = self.add_custom_website(
                    context, {"community_id": community.id, "website": website}
                )
                if err:
                    raise Exception("Failed to save custom website: " + str(err))

            # clone everything for this community
            homePage = HomePageSettings.objects.filter(is_template=True).first()
            create_default_menu(community)
            images = homePage.images.all()
            # TODO: make a copy of the images instead, then in the home page, you wont have to create new files everytime
            if homePage:
                homePage.pk = None
                homePage.title = f"Welcome to Massenergize, {community.name}!"
                homePage.community = community
                homePage.is_template = False
                homePage.save()
                homePage.images.set(images)

            # now create all the pages
            if not _clone_page_settings(
                AboutUsPageSettings, f"About {community.name}", community
            ):
                raise Exception("Failed to clone settings for AboutUs page")
            if not _clone_page_settings(
                ActionsPageSettings, f"Actions for {community.name}", community
            ):
                raise Exception("Failed to clone settings for Actions page")
            if not _clone_page_settings(
                ContactUsPageSettings, f"Contact Us - {community.name}", community
            ):
                raise Exception("Failed to clone settings for ContactUs page")
            if not _clone_page_settings(
                DonatePageSettings, f"Support {community.name}", community
            ):
                raise Exception("Failed to clone settings for Donate page")
            if not _clone_page_settings(
                ImpactPageSettings, f"Our Impact - {community.name}", community
            ):
                raise Exception("Failed to clone settings for Impact page")
            if not _clone_page_settings(
                TeamsPageSettings, f"Teams in this community", community
            ):
                raise Exception("Failed to clone settings for Teams page")
            if not _clone_page_settings(
                VendorsPageSettings, f"Service Providers", community
            ):
                raise Exception("Failed to clone settings for Vendors page")
            if not _clone_page_settings(
                EventsPageSettings, f"Events and Campaigns", community
            ):
                raise Exception("Failed to clone settings for Events page")
            if not _clone_page_settings(
                TestimonialsPageSettings, f"Testimonials", community
            ):
                raise Exception("Failed to clone settings for Testimonials page")
            if not _clone_page_settings(RegisterPageSettings, f"Register", community):
                raise Exception("Failed to clone settings for Register page")
            if not _clone_page_settings(SigninPageSettings, f"Signin", community):
                raise Exception("Failed to clone settings for Signin page")

            admin_group_name = f"{community.name}-{community.subdomain}-Admin-Group"
            comm_admin: CommunityAdminGroup = CommunityAdminGroup.objects.create(
                name=admin_group_name, community=community
            )
            comm_admin.save()

            if context.user_id:
                user = UserProfile.objects.filter(pk=context.user_id).first()
                if user:
                    comm_admin.members.add(user)
                    comm_admin.save()

                    if not user.is_super_admin:
                        user.is_community_admin = True
                    user.communities.add(community)
                    user.save()

            owner_email = args.get("owner_email", None)
            if owner_email:
                owner = UserProfile.objects.filter(email=owner_email)
                owner.update(is_community_admin=True)
                owner = owner.first()
                if owner:
                    comm_admin.members.add(owner)
                    comm_admin.save()
                    owner.communities.add(community)

                    if not owner.is_super_admin:
                        owner.is_community_admin = True
                    owner.communities.add(community)
                    owner.save()
                if contact_sender_alias and owner_email.split("@")[1] not in PUBLIC_EMAIL_DOMAINS:
                     res = add_sender_signature(owner_email, contact_sender_alias, community.owner_name, community.name)

                     if res.status_code == 200:
                        community.contact_info = {
                            "nudge_count": 1,
                            "is_validated": res.json()["Confirmed"],
                            "sender_signature_id": res.json()["ID"]
                        }
                        community.save()



            # Also clone all template actions for this community
            # 11/1/20 BHN: Add protection against excessive copying in case of too many actions marked as template
            # Also don't copy the ones marked as deleted!
            global_actions = Action.objects.filter(is_deleted=False, is_global=True)
            MAX_TEMPLATE_ACTIONS = 25
            num_copied = 0

            actions_copied = set()
            for action_to_copy in global_actions:
                old_tags = action_to_copy.tags.all()
                old_vendors = action_to_copy.vendors.all()
                new_action: Action = action_to_copy
                new_action.pk = None
                new_action.is_published = False
                new_action.is_global = False

                old_title = new_action.title
                new_title = get_new_title(community, old_title)

                # first check that we have not copied an action with the same name
                if new_title in actions_copied:
                    continue
                else:
                    actions_copied.add(new_title)

                new_action.title = new_title

                new_action.save()
                new_action.tags.set(old_tags)
                new_action.vendors.set(old_vendors)

                new_action.community = community
                new_action.save()
                num_copied += 1
                if num_copied >= MAX_TEMPLATE_ACTIONS:
                    break

            # ----------------------------------------------------------------
            # Spy.create_community_footage(communities = [community], related_users=[owner,user], context = context, type = FootageConstants.create(),notes =f"Community ID({community.id})")
            # ----------------------------------------------------------------
            return community, None
        except Exception as e:
            if community:
                # if we did not succeed creating the community we should delete it
                community.delete()
                reserved = Subdomain.objects.filter(name=args.get("subdomain")).first()
                if reserved:
                    reserved.delete()
            log.error(e)
            return None, CustomMassenergizeError(e)

    def update_community(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_id = args.pop("community_id", None)
            website = args.pop("website", None)
            logo = args.pop("logo", None)
            owner_email = args.get("owner_email", None)

            # admins shouldn't be able to update data of other communities
            if not is_admin_of_community(context, community_id):
                return None, NotAuthorizedError()
            
            if not context.user_is_super_admin:
                args = remove_cadmin_locked_fields(args)
              

            # The set of zipcodes, stored as Location models, are what determines a boundary for a geograpically focussed community
            # This will work for the large majority of cases, but there may be some where a zip code overlaps a town or state boundary
            # These we can deal with by having the Location include city and or state fields
            locations = args.pop("locations", None)
            contact_sender_alias = args.get("contact_sender_alias", None)

            favicon = args.pop("favicon", None)
            filter_set = Community.objects.filter(id=community_id)
            if not filter_set:
                return None, InvalidResourceError()

            # let's make sure we can use this subdomain
            subdomain = args.get("subdomain", None)
            if subdomain and not can_use_this_subdomain(subdomain, filter_set.first()):
                raise Exception(
                    "Subdomain is already reserved.  Please, choose a different subdomain"
                )
            
            community = filter_set.first()
            # if user updates owner_email we need to update the signature on postmark
            if owner_email and owner_email != community.owner_email:
                if owner_email.split("@")[1] not in PUBLIC_EMAIL_DOMAINS:
                    name = contact_sender_alias or community.contact_sender_alias or community.name
                    res =  add_sender_signature(owner_email, name, community.owner_name, community.name)
                    if res.status_code == 200:
                        args["contact_info"] = {
                            "nudge_count": 1,
                            "is_validated": res.json()["Confirmed"],
                            "sender_signature_id": res.json()["ID"]
                        }

            if contact_sender_alias and contact_sender_alias != community.contact_sender_alias:
                contact_info = community.contact_info or {}
                sender_signature_id = contact_info.get("sender_signature_id")
                if sender_signature_id:
                   update_sender_signature(sender_signature_id, contact_sender_alias)

            filter_set.update(**args)
            community = filter_set.first()

            # TODO: check that locations have changed before going through the effort of

            geographic = args.get("is_geographically_focused", False)
            if geographic and locations:
                geography_type = args.get("geography_type", None)
                if self._are_locations_updated(geography_type, locations, community):
                    self._update_locations(geography_type, locations, community)
                    self._update_real_estate_units_with_community(community)
            if logo:
                if logo == RESET:
                    community.logo = None
                    community.save()
                else:
                    cLogo = Media.objects.filter(id=logo).first()
                    community.logo = cLogo
                    community.save()

            if favicon:
                cFavicon = Media(
                    file=favicon, name=f"{args.get('name', '')} CommunityFavicon"
                )
                cFavicon.save()
                community.favicon = cFavicon
                community.save()


            if owner_email:
                owner = UserProfile.objects.filter(email=owner_email)
                owner.update(is_community_admin=True)
                owner = owner.first()
                if owner:
                    comm_admin = CommunityAdminGroup.objects.get(community=community)
                    comm_admin.members.add(owner)
                    comm_admin.save()
                    owner.communities.add(community)

                    if not owner.is_super_admin:
                        owner.is_community_admin = True
                    owner.save()
            

            # let's make sure we reserve this subdomain
            if subdomain:
                reserve_subdomain(subdomain, community)

            # save custom website if specified
            # if website:
            ret, err = self.add_custom_website(context, {"community_id": community.id, "website": website})
            if err:
                raise Exception("Failed to save custom website: " + str(err))

            # ----------------------------------------------------------------
            Spy.create_community_footage(
                communities=[community],
                context=context,
                type=FootageConstants.update(),
                notes=f"Community ID({community_id})",
            )
            # ----------------------------------------------------------------
            return community, None

        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def delete_community(self, args, context) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            communities = Community.objects.filter(**args)
            if len(communities) > 1:
                return None, CustomMassenergizeError(
                    "You cannot delete more than one community at once"
                )
            for c in communities:
                # don;t delete the template community: this probably doesn't matter since we don't use template communities for anything
                if "template" in c.name.lower():
                    return None, CustomMassenergizeError(
                        "You cannot delete a template community"
                    )

                # subdomain and custom community website entries will be deleted by virtue of the foreign key CASCADE on deletion
                # delete the goals, assuming they exist, which doesn't have the same link back to community.
                if c.goal:
                    c.goal.delete()
            ids = [c.id for c in communities]
            communities.delete()
            # communities.update(is_deleted=True)

            # ----------------------------------------------------------------
            Spy.create_community_footage(
                communities=communities,
                context=context,
                type=FootageConstants.delete(),
                notes=f"Deleted ID({str(ids)}",
            )
            # ----------------------------------------------------------------
            return communities, None
        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def fetch_admins_of(
        self,args,context: Context
    ) -> Tuple[list, MassEnergizeAPIError]:
        community_ids = args.get("community_ids",[])
        comms = CommunityAdminGroup.objects.filter(community__id__in = community_ids )
        # communities = Community.objects.filter(is_published=True).order_by("name")
        return comms, None
    
    def list_other_communities_for_cadmin(
        self, context: Context
    ) -> Tuple[list, MassEnergizeAPIError]:
        filter_params = get_communities_filter_params(context.get_params())

        user = UserProfile.objects.get(pk=context.user_id)
        # admin_groups = user.communityadmingroup_set.all()
        # ids = [a.community.id for a in admin_groups]
        # communities = Community.objects.filter(is_published=True).exclude(id__in = ids).order_by("name")
        communities = Community.objects.filter(is_published=True).order_by("name")
        return communities, None

    def list_communities_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            # if not context.user_is_community_admin and not context.user_is_community_admin:
            #   return None, CustomMassenergizeError("You are not a super admin or community admin")
            if context.user_is_super_admin:
                return self.list_communities_for_super_admin(context, args)
            elif context.user_is_community_admin:
                filter_params = get_communities_filter_params(context.get_params())


                user = UserProfile.objects.get(pk=context.user_id)
                admin_groups = user.communityadmingroup_set.all()
                communities = [a.community for a in admin_groups]
                communities = list(Community.objects.filter(id__in={com.id for com in communities}).filter(*filter_params).order_by('name'))
                return communities, None
            else:
                return [], None

        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def list_communities_for_super_admin(self, context, args={}):
        try:
            community_ids = args.get("community_ids", [])
            # if not context.user_is_community_admin and not context.user_is_community_admin:
            #   return None, CustomMassenergizeError("You are not a super admin or community admin")
            filter_params = get_communities_filter_params(context.get_params())
            if community_ids:
                communities = list(Community.objects.filter(id__in=community_ids, is_deleted=False, *filter_params).order_by('name'))
                return communities, None

            # the order_by didn't work properly until I added list(), due to "lazy evaluation"
            communities = list(Community.objects.filter(is_deleted=False, *filter_params).order_by('name'))
            return communities, None
        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def add_custom_website(self, context, args):
        try:
            community = get_community_or_die(context, args)
            website = args.get("website", None)

            # give a way to delete the website
            if website == None or website == "" or website == "None":
            
                CustomCommunityWebsiteDomain.objects.filter( community=community).delete()
                return None, None
            
            website = strip_website(website)

            # There can be only one custom website domain for a community site
            # if a different community website domain exists, modify it.
            community_website = CustomCommunityWebsiteDomain.objects.filter(community=community).first()
            if not community_website:
                community_website = CustomCommunityWebsiteDomain(website=website, community=community)
                community_website.save()
            elif community_website.website != website:
                community_website.website = website
                community_website.save()

            return community_website, None
        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def get_graphs(self, context, community_id):
        try:
            if not community_id:
                return [], None
            graphs = Graph.objects.filter(is_deleted=False, community__id=community_id)
            return graphs, None
        except Exception as e:
            log.error(e)
            return None, CustomMassenergizeError(e)

    def list_actions_completed(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            # list actions completed by members of a community or team.  Include any actions which are DONE or TODO (so not really completed)
            # include actions from other communities that users in this community completed on their homes

            # TODO: Normal list causing pagination to throw exceptions: will fix this issue
            time_range = args.get("time_range", "")
            start_date = args.get("start_date", "")
            end_date = args.get("end_date", "")

            actions_completed = []
            if not context.is_admin_site:
                community = get_community_or_die(context, args)
                actions_completed = count_action_completed_and_todos(
                    communities=[community],
                    time_range=time_range,
                    start_date=start_date,
                    end_date=end_date,
                )
            else:
                communities = args.get("communities", [])
                if (
                    len(communities)
                    and communities[0] == ALL
                    and context.user_is_community_admin
                ):
                    user = UserProfile.objects.filter(email=context.user_email).first()
                    groups = user.communityadmingroup_set.all()
                    communities = [ag.community.id for ag in groups]
                elif (
                    len(communities)
                    and communities[0] == ALL
                    and context.user_is_super_admin
                ):
                    communities = None

                actions = args.get("actions", [])
                actions_completed = count_action_completed_and_todos(
                    communities=communities,
                    actions=actions,
                    time_range=time_range,
                    start_date=start_date,
                    end_date=end_date,
                )

            return actions_completed, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_community_features(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_id = args.get("community_id")
            if not community_id:
                return None, CustomMassenergizeError("community_id is required")
            
            community = Community.objects.get(id=community_id)
            
            current_date_and_time = datetime.now(timezone.utc)
            feature_flags = FeatureFlag.objects.filter(Q(expires_on__gt=current_date_and_time) | Q(expires_on=None), allow_opt_in=True)
            
            obj = {}
            for feature_flag in feature_flags:
                enabled_communities = feature_flag.enabled_communities()
                obj[feature_flag.key] = {
                    "key": feature_flag.key,
                    "notes": feature_flag.notes,
                    "is_enabled": community in enabled_communities,
                    'name': feature_flag.name
                }
            
            return obj, None
        
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def request_feature_for_community(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_id = args.get("community_id")
            feature_flag_key = args.get("feature_flag_key")
            should_enable = args.get("enable")
            user = get_user_from_context(context)
            
            if not community_id:
                return None, CustomMassenergizeError("community_id is required")
            
            if not feature_flag_key:
                return None, CustomMassenergizeError("feature_flag_key is required")
            
            try:
                community = Community.objects.get(id=community_id)
            except Community.DoesNotExist:
                return None, CustomMassenergizeError(f"Community with id {community_id} not found")
            
            feature_flag = FeatureFlag.objects.get(key=feature_flag_key)
            if not feature_flag:
                return None, CustomMassenergizeError(f"FeatureFlag with key {feature_flag_key} not found")
            
            check_community_membership(feature_flag, should_enable, community)
            
            if should_enable:
                if IS_PROD:
                    send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL,{"text":f"{user.full_name if user else context.user_email} requested '{feature_flag.name}' to be enabled for {community.name} "})
            else:
                if IS_PROD:
                    send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text":f"{user.full_name if user else context.user_email} requested {feature_flag.name} to be disabled for {community.name} "})
            
            return {"key": feature_flag.key, "notes": feature_flag.notes, "is_enabled": should_enable, "name":feature_flag.name}, None
        
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_community_notification_settings(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            notification_setting_id = args.get("id")
            is_active = args.get("is_active", False)
            activate_on = args.get("activate_on")
            user = get_user_from_context(context)

            if not notification_setting_id:
                return None, CustomMassenergizeError("id is required")

            notification_setting = CommunityNotificationSetting.objects.filter(id=notification_setting_id).first()
            if not notification_setting:
                return None, CustomMassenergizeError("Community notification settings with ID not found")
            
            if not context.user_is_super_admin:
                if not is_admin_of_community(context, notification_setting.community.id):
                    return None, NotAuthorizedError()

            notification_setting.is_active = is_active
            notification_setting.activate_on = activate_on
            notification_setting.updated_by = user
            notification_setting.save()
            
            if activate_on:
                more_info = notification_setting.more_info or {}
                task_id = more_info.get("task_id")
                if task_id:
                    AsyncResult(task_id).revoke()
                
                eta = datetime.strptime(activate_on, "%Y-%m-%d") + timedelta(minutes=0)
                
                task_id = automatically_activate_nudge.apply_async(args=[notification_setting.id], eta=eta).id
                notification_setting.more_info = {**more_info, "task_id": task_id}
                notification_setting.save()
            
            if not is_active and not activate_on:
                more_info = notification_setting.more_info or {}
                task_id = more_info.get("task_id")
                if task_id:
                    AsyncResult(task_id).revoke()
                    notification_setting.more_info = {**more_info, "task_id": None}
                    notification_setting.save()
            
            # ----------------------------------------------------------------
            notification_type = notification_setting.notification_type.split('-feature-flag')[0]
            Spy.create_community_notification_settings_footage(communities=[notification_setting.community], context=context,type=FootageConstants.update(), notes=f"{notification_type} ID({notification_setting_id})")
            # ----------------------------------------------------------------
            
            return {"feature_is_enabled": True, **notification_setting.simple_json()}, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_community_notification_settings(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community_id = args.get("community_id")
            
            if not community_id:
                return None, CustomMassenergizeError("community_id is required")
            
            community = Community.objects.filter(id=community_id).prefetch_related("notification_settings").first()
            
            if not community:
                return None, CustomMassenergizeError("Community not found")
            
            if not is_admin_of_community(context, community.id):
                return None, NotAuthorizedError()
            
            settings_dict = {setting.notification_type: setting for setting in community.notification_settings.all()}
            feature_flags = FeatureFlag.objects.filter(key__in=COMMUNITY_NOTIFICATION_TYPES)
            
            new_settings = []
            resulting_settings = {}
            
            for flag in feature_flags:
                setting = settings_dict.get(flag.key)
                feature_is_enabled = flag.is_enabled_for_community(community)
                
                if setting is None:
                    new_setting = CommunityNotificationSetting(community=community, notification_type=flag.key, is_active=True)
                    
                    new_settings.append(new_setting)
                    setting = new_setting
                
                resulting_settings[flag.key] = {"feature_is_enabled": feature_is_enabled, **setting.simple_json()}
            
            if new_settings:
                CommunityNotificationSetting.objects.bulk_create(new_settings)
            
            return resulting_settings, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
    
    def list_communities_feature_flags(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            community_id = args.get("community_id")
            subdomain = args.get("subdomain")
            
            if community_id or subdomain:
                community, _ = get_community(community_id, subdomain)
                
                if not community:
                    return None, CustomMassenergizeError("Community not found")
                
                return get_enabled_flags(community), None
            else:
                # check if user is a community admin, get all communities they are admin of
                user = get_user_from_context(context)
                if not user:
                    return None, CustomMassenergizeError("User not found")
                
                communities = user.communityadmingroup_set.all().values_list("community__id", flat=True)
            
            feature_flags = FeatureFlag.objects.filter(
                Q(audience=FeatureFlagConstants().for_everyone()) |
                Q(audience=FeatureFlagConstants().for_specific_audience(), communities__id__in=communities) |
                (Q(audience=FeatureFlagConstants().for_all_except()) & ~Q(communities__id__in=communities))
            ).exclude(expires_on__lt=datetime.now(timezone.utc)).prefetch_related('communities')
            
            ff = []
            for flag in feature_flags:
                ff.append({
                    "key": flag.key,
                    "name": flag.name,
                    "communities": None if subdomain or community_id else [c.id for c in flag.enabled_communities() if c.id in communities]
                })
            
            return ff, None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
    
    
########### Helper functions  ###########


def can_use_this_subdomain(subdomain: str, community: Community = None) -> bool:
    subdomain = subdomain.lower()

    if subdomain in RESERVED_SUBDOMAIN_LIST:
        return False

    if not Subdomain.objects.filter(name=subdomain).exists():
        return True

    # a community should be able to reuse an old domain of theirs
    if (
        community
        and Subdomain.objects.filter(name=subdomain, community=community).exists()
    ):
        return True

    return False


def reserve_subdomain(subdomain: str, community: Community = None):
    if not community:
        raise Exception("community is required to set a subdomain")

    # if we are here then the subdomain is available to be used by this community
    # now let's make sure it is all lower case
    subdomain = subdomain.lower()

    # if subdomain is in use for this community just return right away
    if Subdomain.objects.filter(
        community=community, name__iexact=subdomain, in_use=True
    ):
        return

    # first check that we can use this domain
    if not can_use_this_subdomain(subdomain, community):
        raise Exception(f"This community cannot reserve the subdomain: {subdomain}")

    # mark the old subdomains for this community to un-used
    Subdomain.objects.filter(community=community, in_use=True).update(in_use=False)

    # let's do a search for this subdomain
    subdomain_search = Subdomain.objects.filter(name__iexact=subdomain)
    if subdomain_search.exists():
        # because we call can_use_this_subdomain() above, we know that:
        #  if we get here then the community owns this domain already.
        # If another community owned this domain we would have raised an exception
        # Hence we can go ahead and update this this subdomain to in-use
        subdomain_search.update(in_use=True)
    else:
        # if subdomain does not exist then we need to create a new one
        new_subdomain = Subdomain(name=subdomain, community=community, in_use=True)
        new_subdomain.save()