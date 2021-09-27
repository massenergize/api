from database.models import (
    Community,
    CommunityMember,
    UserProfile,
    Action,
    Event,
    Graph,
    Media,
    ActivityLog,
    AboutUsPageSettings,
    ActionsPageSettings,
    ContactUsPageSettings,
    DonatePageSettings,
    HomePageSettings,
    ImpactPageSettings,
    TeamsPageSettings,
    EventsPageSettings,
    TestimonialsPageSettings,
    VendorsPageSettings,
    Goal,
    CommunityAdminGroup,
    Subdomain,
)
from database.models import (
    Community,
    CommunityMember,
    UserProfile,
    Action,
    Event,
    Graph,
    Media,
    ActivityLog,
    AboutUsPageSettings,
    ActionsPageSettings,
    ContactUsPageSettings,
    DonatePageSettings,
    HomePageSettings,
    ImpactPageSettings,
    TeamsPageSettings,
    Goal,
    CommunityAdminGroup,
    Location,
    RealEstateUnit,
)
from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
    InvalidResourceError,
    ServerError,
    CustomMassenergizeError,
)
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.store.graph import GraphStore
from django.db.models import Q
from .utils import (
    get_community_or_die,
    get_user_or_die,
    get_new_title,
    is_reu_in_community,
    check_location,
)
from database.utils.common import json_loader
from _main_.utils.constants import RESERVED_SUBDOMAIN_LIST
from typing import Tuple
import zipcodes
from sentry_sdk import capture_message, capture_exception


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
                    else:
                        raise Exception("No zip code entry found for zip=" + location)

                    # get_or_create gives an error if multiple such locations exist (which can happen)
                    # loc, created = Location.objects.get_or_create(location_type='ZIP_CODE_ONLY', zipcode=location, city=city)
                    loc = Location.objects.filter(
                        location_type="ZIP_CODE_ONLY", zipcode=location, city=city
                    )
                    if not loc:
                        loc = Location.objects.create(
                            location_type="ZIP_CODE_ONLY", zipcode=location, city=city
                        )
                        print("Zipcode " + location + " created for town " + city)
                    else:
                        loc = loc.first()
                        print("Zipcode " + location + " found for town " + city)

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
                    print("Number of zipcodes = " + str(len(zips)))
                    if len(zips) > 0:
                        for zip in zips:
                            print(zip)
                            zipcode = zip["zip_code"]

                            # get_or_create gives an error if multiple such locations exist (which can happen)
                            # loc, created = Location.objects.get_or_create(location_type='ZIP_CODE_ONLY', zipcode=location, city=city)
                            loc = Location.objects.filter(
                                location_type="ZIP_CODE_ONLY",
                                zipcode=location,
                                city=town,
                            )
                            if not loc:
                                loc = Location.objects.create(
                                    location_type="ZIP_CODE_ONLY",
                                    zipcode=location,
                                    city=town,
                                )
                                print("Zipcode " + zipcode + " created")
                            else:
                                loc = loc.first()
                                print("Zipcode " + zipcode + " found")

                            self._check_geography_unique(
                                community, geography_type, zipcode
                            )

                    else:
                        print(
                            "No zipcodes found corresponding to town "
                            + town
                            + ", "
                            + state
                        )
                        raise Exception(
                            "No zipcodes found corresponding to city "
                            + town
                            + ", "
                            + state
                        )
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
                print("Number of zipcodes = " + str(len(zips)))
                if len(zips) > 0:
                    # get_or_create gives an error if multiple such locations exist (which can happen)
                    # loc, created = Location.objects.get_or_create(location_type='ZIP_CODE_ONLY', zipcode=location, city=city)
                    loc = Location.objects.filter(
                        location_type="CITY_ONLY", city=city, state=state
                    )
                    if not loc:
                        loc = Location.objects.create(
                            location_type="CITY_ONLY", city=city, state=state
                        )
                        print("City " + city + " created")
                    else:
                        loc = loc.first()
                        print("City " + city + " found")

                else:
                    print(
                        "No zipcodes found corresponding to city " + city + ", " + state
                    )
                    raise Exception(
                        "No zipcodes found corresponding to city " + city + ", " + state
                    )

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
                    county=town, state=state, zip_code_type="STANDARD"
                )
                print("Number of zipcodes = " + str(len(zips)))
                if len(zips) > 0:
                    # get_or_create gives an error if multiple such locations exist (which can happen)
                    # loc, created = Location.objects.get_or_create(location_type='ZIP_CODE_ONLY', zipcode=location, city=city)
                    loc = Location.objects.filter(
                        location_type="COUNTY_ONLY", county=county, state=state
                    )
                    if not loc:
                        loc = Location.objects.create(
                            location_type="COUNTY_ONLY", county=county, state=state
                        )
                        print("County " + county + " created")
                    else:
                        loc = loc.first()
                        print("County " + county + " found")

                else:
                    print(
                        "No zipcodes found corresponding to county "
                        + county
                        + ", "
                        + state
                    )
                    raise Exception(
                        "No zipcodes found corresponding to county "
                        + county
                        + ", "
                        + state
                    )

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
                        print("State " + state + " created")
                    else:
                        loc = loc.first()
                        print("State " + state + " found")
                else:
                    print("No zipcodes found corresponding to state " + location)
                    raise Exception(
                        "No zipcodes found corresponding to state " + location
                    )

                self._check_geography_unique(community, geography_type, location)

            elif geography_type == "COUNTRY":
                # check that this state is found in the zipcodes list
                country = location
                zips = zipcodes.filter_by(country=country, zip_code_type="STANDARD")
                print("Number of zipcodes = " + str(len(zips)))
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
                        print("Country " + country + " created")
                    else:
                        loc = loc.first()
                        print("Country " + country + " found")
                else:
                    print("No zipcodes found corresponding to country " + location)
                    raise Exception(
                        "No zipcodes found corresponding to country " + location
                    )

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

    def get_community_info(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            subdomain = args.get("subdomain", None)
            community_id = args.get("id", None)

            if not community_id and not subdomain:
                return None, CustomMassenergizeError(
                    "Missing community_id or subdomain field"
                )

            community: Community = (
                Community.objects.select_related("logo", "favicon", "goal")
                .filter(Q(pk=community_id) | Q(subdomain=subdomain))
                .first()
            )
            if not community:
                return None, InvalidResourceError()

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

                    goal = community.goal
                    total = ( 
                        goal.attained_number_of_households 
                        + goal.attained_number_of_actions 
                        + goal.attained_carbon_footprint_reduction
                    )

                    goal.attained_number_of_households = max(category_totals)                    
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
            capture_exception(e)
            return None, CustomMassenergizeError(e)

    def join_community(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community = get_community_or_die(context, args)
            user = get_user_or_die(context, args)
            user.communities.add(community)
            user.save()

            community_member: CommunityMember = CommunityMember.objects.filter(
                community=community, user=user
            ).first()
            if not community_member:
                community_member = CommunityMember.objects.create(
                    community=community, user=user, is_admin=False
                )

            return user, None
        except Exception as e:
            capture_exception(e)
            return None, CustomMassenergizeError(e)

    def leave_community(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            community = get_community_or_die(context, args)
            user = get_user_or_die(context, args)
            user.communities.remove(community)
            user.save()

            community_member: CommunityMember = CommunityMember.objects.filter(
                community=community, user=user
            ).first()
            if not community_member or (not community_member.is_admin):
                community_member.delete()

            return user, None
        except Exception as e:
            capture_exception(e)
            return None, CustomMassenergizeError(e)

    def list_communities(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if context.is_sandbox:
                communities = Community.objects.filter(
                    is_deleted=False, is_approved=True
                ).exclude(subdomain="template")
            else:
                communities = Community.objects.filter(
                    is_deleted=False, is_approved=True, is_published=True
                ).exclude(subdomain="template")

            if not communities:
                return [], None
            return communities, None
        except Exception as e:
            capture_exception(e)
            return None, CustomMassenergizeError(e)

    def create_community(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        community = None
        try:
            subdomain = args.get('subdomain')
            if not can_use_this_subdomain(subdomain):
                raise Exception("Subdomain is already reserved.  Please, choose a different subdomain")

            logo = args.pop("logo", None)

            # The set of locations (zipcodes, cities, counties, states), stored as Location models, are what determines a boundary for a geograpically focussed community
            # This will work for the large majority of cases, but there may be some where a zip code overlaps a town or state boundary
            # These we can deal with by having the Location include city and or state fields
            locations = args.pop("locations", None)

            favicon = args.pop("favicon", None)
            community = Community.objects.create(**args)
            community.save()

            geographic = args.get("is_geographically_focused", False)
            if geographic:
                geography_type = args.get("geography_type", None)
                self._update_locations(geography_type, locations, community)
                self._update_real_estate_units_with_community(community)

            if logo:
                cLogo = Media(file=logo, name=f"{args.get('name', '')} CommunityLogo")
                cLogo.save()
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

            homePage = HomePageSettings.objects.filter(is_template=True).first()
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

            owner_email = args.get("owner_email", None)
            if owner_email:
                owner = UserProfile.objects.filter(email=owner_email).first()
                if owner:
                    comm_admin.members.add(owner)
                    comm_admin.save()

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


            reserve_subdomain(subdomain, community)
            return community, None
        except Exception as e:
            if community:
                # if we did not succeed creating the community we should delete it
                community.delete()
            capture_exception(e)
            return None, CustomMassenergizeError(e)

    def update_community(self, community_id, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            logo = args.pop("logo", None)

            # The set of zipcodes, stored as Location models, are what determines a boundary for a geograpically focussed community
            # This will work for the large majority of cases, but there may be some where a zip code overlaps a town or state boundary
            # These we can deal with by having the Location include city and or state fields
            locations = args.pop("locations", None)

            favicon = args.pop("favicon", None)
            filter_set = Community.objects.filter(id=community_id)
            if not filter_set:
                return None, InvalidResourceError()

            # let's make sure we can use this subdomain
            subdomain = args.get('subdomain', None)
            if subdomain and not can_use_this_subdomain(subdomain, filter_set.first()):
                raise Exception("Subdomain is already reserved.  Please, choose a different subdomain")

            filter_set.update(**args)
            community = filter_set.first()

            # TODO: check that locations have changed before going through the effort of

            geographic = args.get("is_geographically_focused", False)
            if geographic:
                geography_type = args.get("geography_type", None)
                self._update_locations(geography_type, locations, community)
                self._update_real_estate_units_with_community(community)

            if logo:
                cLogo = Media(file=logo, name=f"{args.get('name', '')} CommunityLogo")
                cLogo.save()
                community.logo = cLogo
                community.save()

            if favicon:
                cFavicon = Media(
                    file=favicon, name=f"{args.get('name', '')} CommunityFavicon"
                )
                cFavicon.save()
                community.favicon = cFavicon
                community.save()

            # let's make sure we reserve this subdomain
            reserve_subdomain(subdomain, community)
            
            return community, None

        except Exception as e:
            capture_exception(e)
            return None, CustomMassenergizeError(e)

    def delete_community(self, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            communities = Community.objects.filter(**args)
            if len(communities) > 1:
                return None, CustomMassenergizeError(
                    "You cannot delete more than one community at once"
                )
            for c in communities:
                if "template" in c.name.lower():
                    return None, CustomMassenergizeError(
                        "You cannot delete a template community"
                    )

            communities.delete()
            # communities.update(is_deleted=True)
            return communities, None
        except Exception as e:
            capture_exception(e)
            return None, CustomMassenergizeError(e)

    def list_communities_for_community_admin(
        self, context: Context
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            # if not context.user_is_community_admin and not context.user_is_community_admin:
            #   return None, CustomMassenergizeError("You are not a super admin or community admin")
            if context.user_is_super_admin:
                return self.list_communities_for_super_admin(context)
            elif context.user_is_community_admin:
                user = UserProfile.objects.get(pk=context.user_id)
                admin_groups = user.communityadmingroup_set.all()
                return [a.community for a in admin_groups], None
            else:
                return [], None

        except Exception as e:
            capture_exception(e)
            return None, CustomMassenergizeError(e)

    def list_communities_for_super_admin(self, context):
        try:
            # if not context.user_is_community_admin and not context.user_is_community_admin:
            #   return None, CustomMassenergizeError("You are not a super admin or community admin")

            communities = Community.objects.filter(is_deleted=False)
            return communities, None
        except Exception as e:
            capture_exception(e)
            return None, CustomMassenergizeError(str(e))

    def get_graphs(self, context, community_id):
        try:
            if not community_id:
                return [], None
            graphs = Graph.objects.filter(is_deleted=False, community__id=community_id)
            return graphs, None
        except Exception as e:
            capture_exception(e)
            return None, CustomMassenergizeError(str(e))


########### Helper functions  ###########

def can_use_this_subdomain(subdomain: str, community: Community=None) -> bool:
    subdomain = subdomain.lower()

    if subdomain in RESERVED_SUBDOMAIN_LIST:
        return False

    if not Subdomain.objects.filter(name=subdomain).exists():
        return True
    
    # a community should be able to reuse an old domain of theirs
    if community and Subdomain.objects.filter(name=subdomain, community=community).exists():
        return True

    return False

def reserve_subdomain(subdomain: str, community: Community=None):
    if not community:
        raise Exception('community is required to set a subdomain')

    # if we are here then the subdomain is available to be used by this community
    # now let's make sure it is all lower case
    subdomain = subdomain.lower()

    # if subdomain is in use for this community just return right away
    if Subdomain.objects.filter(community=community, subdomain__iexact=subdomain, in_use=True).update(in_use=False):
        return

    # first check that we can use this domain 
    if not can_use_this_subdomain(subdomain, community):
        raise Exception(f'This community cannot reserve the subdomain: {subdomain}')


    # mark the old subdomains for this community to un-used
    Subdomain.objects.filter(community=community, in_use=True).update(in_use=False)
    
    # let's do a search for this subdomain 
    subdomain_search = Subdomain.objects.filter(subdomain__iexact=subdomain)
    if subdomain_search.exists():
        # because we call can_use_this_subdomain() above, we know that if we 
        # here then the community owns this domain already.  If another community owned
        # this domain we would have raised an exception
        # Hence we can go ahead and update this this subdomain to in-use
        subdomain_search.update(in_use=True)
    else:
        # if subdomain does not exist then we need to create a new one
        new_subdomain = Subdomain(name=subdomain, community=community, in_use=True)
        new_subdomain.save()

