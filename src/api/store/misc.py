from typing import Tuple

from _main_.utils.massenergize_logger import log

from _main_.utils.context import Context
from _main_.utils.footage.spy import Spy
from _main_.utils.massenergize_errors import (
    CustomMassenergizeError,
    InvalidResourceError,
    MassEnergizeAPIError,
)
from _main_.utils.utils import load_json
from api.tests.common import createUsers
from api.utils.api_utils import load_default_menus_from_json, \
    remove_unpublished_items, validate_menu_content
from database.models import Action, CarbonEquivalency, Community, CommunityAdminGroup, CommunityMember, Data, Event, \
    HomePageSettings, Location, Media, Menu, RealEstateUnit, Subdomain, TagCollection, Team, TeamMember, UserActionRel, \
    UserProfile, Vendor
from database.utils.common import json_loader
from .utils import check_location, find_reu_community, get_community, split_location_string


class MiscellaneousStore:
    def __init__(self):
        self.name = "Miscellaneous Store/DB"
        #self.list_commonly_used_icons()

    def fetch_footages(self,context:Context, args): 
        footages = None 
        try:
            if context.user_is_super_admin: 
                footages = Spy.fetch_footages_for_super_admins(context = context)
            else: 
                footages = Spy.fetch_footages_for_community_admins(context = context)

            return footages, None
        except Exception as e: 
            return None, str(e)


    def authenticateFrontendInTestMode(self, args): 
        email = args.get("email"); 
        user = UserProfile.objects.filter(email = email).first() 
        if not user: 
            user = createUsers(email = email, full_name = "Master Chef - Test")
        return user, None
        
    def remake_navigation_menu(self, json) -> Tuple[dict, MassEnergizeAPIError]:
        Menu.objects.all().delete()
        for name, menu in json.items():
            new_menu = Menu(name=name, content=menu)
            try:
                new_menu.save()
            except:
                return {}, "Sorry, could not remake menu"
        return json or {}, None

    def navigation_menu_list(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            main_menu = Menu.objects.all()
            return main_menu, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def actions_report(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        print("Actions report!")
        total = 0
        total_wo_ccaction = 0
        for c in Community.objects.filter(is_published=True):
            print(c)
            actions = Action.objects.filter(community__id=c.id, is_published=True, is_deleted=False)
            total += actions.count()
            for action in actions:
                if action.calculator_action == None:
                    total_wo_ccaction += 1
                    print(action.title + " has no corresponding CCAction")
        print("Total actions = "+str(total) + ", no CCAction ="+str(total_wo_ccaction))
        return None, None

    def backfill(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        return self.backfill_graph_default_data(context, args), None

    def backfill_subdomans(self):
        for c in Community.objects.all():
            try:
                Subdomain(name=c.subdomain, in_use=True, community=c).save()
            except Exception as e:
                print(e)

    def backfill_teams(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
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

            return {"teams_member_backfill": "done"}, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def backfill_community_members(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            #users = UserProfile.objects.all()
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

            return {"name": "community_member_backfill", "status": "done"}, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def backfill_graph_default_data(self, context: Context, args):
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
                        print(
                            "Backfill: Community: "
                            + community.name
                            + ", Category: "
                            + tag.name
                            + ", Old: "
                            + str(oldval)
                            + ", New: "
                            + str(val)
                        )
            return {"graph_default_data": "done"}, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def backfill_real_estate_units(self, context: Context, args):
        ZIPCODE_FIXES = json_loader("api/store/ZIPCODE_FIXES.json")
        try:
            # BHN - Feb 2021 - assign all real estate units to geographic communities
            # Set the community of a real estate unit based on the location of the real estate unit.
            # This defines what geographic community, if any gets credit
            # For now, check for zip code
            reu_all = RealEstateUnit.objects.all()
            print("Number of real estate units:" + str(reu_all.count()))

            userProfiles = UserProfile.objects.prefetch_related(
                "real_estate_units"
            ).filter(is_deleted=False)
            print("number of user profiles:" + str(userProfiles.count()))

            # loop over profiles and realEstateUnits associated with them
            for userProfile in userProfiles:
                user = userProfile.email
                reus = userProfile.real_estate_units.all()
                msg = "User: %s (%s), %d households - %s" % (
                    userProfile.full_name,
                    userProfile.email,
                    reus.count(),
                    userProfile.created_at.strftime("%Y-%m-%d"),
                )
                print(msg)

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
                            if userProfile.email in ZIPCODE_FIXES:
                                zip = ZIPCODE_FIXES[user]["zipcode"]
                                city = ZIPCODE_FIXES[user]["city"]
                            else:
                                street = loc_parts[0].capitalize()
                                city = loc_parts[1].capitalize()
                                state = loc_parts[2].upper()
                                zip = loc_parts[3].strip()
                                if not zip or (len(zip) != 5 and len(zip) != 10):
                                    print(
                                        "Invalid zipcode: " + zip + ", setting to 00000"
                                    )
                                    zip = "00000"
                                elif len(zip) == 10:
                                    zip = zip[0:5]
                        else:
                            # deal with odd cases which were encountered in the dev database
                            zip = "00000"
                            state = "MA"  # may be wrong occasionally
                            for entry in ZIPCODE_FIXES:
                                if loc.find(entry) >= 0:
                                    zip = ZIPCODE_FIXES[entry]["zipcode"]
                                    city = ZIPCODE_FIXES[entry]["city"]
                                    state = ZIPCODE_FIXES[entry].get("state", "MA")

                            print("Zipcode assigned " + zip)

                        # create the Location for the RealEstateUnit
                        location_type, valid = check_location(
                            street, unit_number, city, state, zip
                        )
                        if not valid:
                            print("check_location returns: " + location_type)
                            continue

                        # newloc, created = Location.objects.get_or_create(
                        newloc = Location.objects.filter(
                            location_type=location_type,
                            street=street,
                            unit_number=unit_number,
                            zipcode=zip,
                            city=city,
                            county=county,
                            state=state,
                        )
                        if not newloc:
                            newloc = Location.objects.create(
                                location_type=location_type,
                                street=street,
                                unit_number=unit_number,
                                zipcode=zip,
                                city=city,
                                county=county,
                                state=state,
                            )
                            print("Zipcode " + zip + " created for town " + city)
                        else:
                            newloc = newloc.first()
                            print("Zipcode " + zip + " found for town " + city)

                        reu.address = newloc
                        reu.save()

                    else:

                        # fixes for some missing addresses in summer Prod DB
                        zip = "00000"
                        cn = ""
                        if userProfile.communities:
                            cn = userProfile.communities.first().name
                        elif reu.community:
                            cn = reu.community.name

                        if cn in ZIPCODE_FIXES:
                            zip = ZIPCODE_FIXES[cn]["zipcode"]
                            city = ZIPCODE_FIXES[cn]["city"]
                        elif user in ZIPCODE_FIXES:
                            zip = ZIPCODE_FIXES[user]["zipcode"]
                            city = ZIPCODE_FIXES[user]["city"]

                        # no location was stored?
                        if zip == "00000":
                            print("No location found for RealEstateUnit " + str(reu))

                        location_type = "ZIP_CODE_ONLY"
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
                            print("Location with zipcode " + zip + " created")
                        else:
                            print("Location with zipcode " + zip + " found")
                        reu.address = newloc
                        reu.save()

                    # determine which, if any, community this household is actually in
                    community = find_reu_community(reu)
                    if community:
                        print(
                            "Adding the REU with zipcode "
                            + zip
                            + " to the community "
                            + community.name
                        )
                        reu.community = community

                    elif reu.community:
                        print(
                            "REU not located in any community, but was labeled as belonging to the community "
                            + reu.community.name
                        )
                        reu.community = None
                    reu.save()

            return {"backfill_real_estate_units": "done"}, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def create_carbon_equivalency(self, args):
        try:
            new_carbon_equivalency = CarbonEquivalency.objects.create(**args)
            return new_carbon_equivalency, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_carbon_equivalency(self, args):
        try:
            id = args.get("id", None)

            carbon_equivalencies = CarbonEquivalency.objects.filter(id=id)

            if not carbon_equivalencies:
                return None, InvalidResourceError()

            carbon_equivalencies.update(**args)
            carbon_equivalency = carbon_equivalencies.first()

            return carbon_equivalency, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def get_carbon_equivalencies(self, args):

        id = args.get("id", None)
        if id:
            carbon_equivalencies = CarbonEquivalency.objects.filter(id=id)
            if not carbon_equivalencies:
                return None, InvalidResourceError()
            else:
                carbon_equivalencies = carbon_equivalencies.first()

        else:
            carbon_equivalencies = CarbonEquivalency.objects.all()
        return carbon_equivalencies, None

    def delete_carbon_equivalency(self, args):
        id = args.get("id", None)
        carbon_equivalency = CarbonEquivalency.objects.filter(id=id)

        if not carbon_equivalency:
            return None, InvalidResourceError()

        carbon_equivalency.delete()
        return carbon_equivalency, None

    def generate_sitemap_for_portal(self):
        return {
            "communities": Community.objects.filter(
                is_deleted=False, is_published=True
            ).values("id", "subdomain", "updated_at"),
            "actions": Action.objects.filter(
                is_deleted=False,
                is_published=True,
                community__is_published=True,
                community__is_deleted=False,
            )
            .select_related("community")
            .values("id", "community__subdomain", "updated_at"),
            "services": Vendor.objects.filter(is_deleted=False, is_published=True)
            .prefetch_related("communities")
            .values("id", "communities__subdomain", "updated_at"),
            "events": Event.objects.filter(
                is_deleted=False,
                is_published=True,
                community__is_published=True,
                community__is_deleted=False,
            )
            .select_related("community")
            .values("id", "community__subdomain"),
        }

    # utility routine to list icons from the database
    def list_commonly_used_icons(self):

        common_icons = {}
        #action.icon
        #button.icon
        #service.icon
        #card.icon
        #tag.icon
        #CarbonEquivalency.icon

        #HomePageSettings.featured_links json
        all_hps = HomePageSettings.objects.all()
        for hps in all_hps:
            if hps.featured_links:
                for item in hps.featured_links:
                    icon = item["icon"]
                    if icon in common_icons.keys():
                        common_icons[icon] += 1
                    else:
                        common_icons[icon] = 1

        sorted_keys = sorted(common_icons, key=common_icons.get, reverse=True)
        for key in sorted_keys:
            print(str(key) + ": " + str(common_icons[key]))

    def load_menu_items(self, context, args):
        try:
            subdomain = args.get("subdomain", None)
            community_id = args.get("community_id", None)

            if not subdomain and not community_id:
                return None, CustomMassenergizeError("No community or subdomain provided")

            community, _ = get_community(community_id=community_id, subdomain=subdomain)
            if not community:
                return None, CustomMassenergizeError("Community not found")
            
            menus = Menu.objects.filter(community=community, is_published=True)
            if not menus:
                return None, CustomMassenergizeError("No menus found for this community")
            
            menu = menus.first()
            
            portal_main_nav_links = remove_unpublished_items(menu.content)
            portal_footer_quick_links = remove_unpublished_items(menu.footer_content.get("links", []))
            
            return [
                {"name": "PortalMainNavLinks", "content": portal_main_nav_links},
                {"name": menu.footer_content.get("name", "PortalFooterQuickLinks"), "content": {"links": portal_footer_quick_links}},
                menu.contact_info
            
            ], None
        
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
        
    def create_menu(self, context, args):
        try:
            community_id = args.pop('community_id', None)
            subdomain = args.pop('subdomain', None)
            
            if not community_id and not subdomain:
                return None, CustomMassenergizeError("community_id or subdomain not provided")
            
            community, error = get_community(community_id=community_id, subdomain=subdomain)
            
            if error:
                return None, error
            
            default_menus = load_default_menus_from_json()
            
            name = f"{community.subdomain} Main Menu"
            args["name"] = name
            args["community"] = community
            args["is_custom"] = True
            args["content"] = default_menus["PortalMainNavLinks"]
            args["footer_content"] = default_menus["PortalFooterQuickLinks"]
            args["contact_info"] = default_menus["PortalFooterContactInfo"]
            
            menu = Menu.objects.create(**args)
            
            return menu, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def update_menu(self, context, args):
        try:
            menu_id = args.pop('id', None)
            content = args.pop('content', None)
            footer_content = args.pop('footer_content', None)
            contact_info = args.pop('contact_info', None)
            
            if not menu_id:
                return None, CustomMassenergizeError("id not provided")
            
            community_logo_id = args.pop('community_logo_id', None)
            
            menu = Menu.objects.filter(id=menu_id)
            
            if not menu:
                return None, CustomMassenergizeError("Menu not found")
            
            args["is_custom"] = True
            
            menu.update(**args)
            
            if content:
            
                is_content_valid = validate_menu_content(content)
                
                if not is_content_valid:
                    return None, CustomMassenergizeError("Invalid menu content")
                menu.update(content=content)

            if footer_content:
                is_footer_content_valid = validate_menu_content(footer_content.get('links', []))
                
                if not is_footer_content_valid:
                    return None, CustomMassenergizeError("Invalid footer content")
                
                menu.update(footer_content=footer_content)
                
            if contact_info:
                menu.update(contact_info=contact_info)
                
            if community_logo_id:
                community = menu.first().community
                community.logo = Media.objects.get(id=community_logo_id)
                community.save()

            return menu.first(), None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
            
    def delete_menu(self, context, args):
        try:
            menu_id = args.pop('id', None)
            menu = Menu.objects.filter(id=menu_id)
            
            if not menu:
                return None, CustomMassenergizeError("Menu not found")
            
            menu = menu.first()
            if not menu.is_custom:
                return None, CustomMassenergizeError("Cannot delete default menu. Try resetting it instead")
            
            menu.delete()
            return True, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
        
    def get_menu(self, context, args):
        try:
            menu_id = args.pop('id', None)
            menu = Menu.objects.filter(id=menu_id)
            
            if not menu:
                return None, CustomMassenergizeError("Menu not found")
                
            return menu.first(), None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
    def get_menus_for_admin(self, context, args):
        try:
            community_id = args.pop('community_id', None)
            subdomain = args.pop('subdomain', None)
            
            if not community_id and not subdomain:
                return None, CustomMassenergizeError("community_id or subdomain not provided")
            
            community, error = get_community(community_id=community_id, subdomain=subdomain)
            
            if error:
                return None, error
            
            menus = Menu.objects.filter(community=community)
            
            return menus, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
        
    def reset_menu(self, context, args):
        try:
            menu_id = args.pop('id', None)
            
            if not menu_id:
                return None, CustomMassenergizeError("id not provided!!")
            
            menu = Menu.objects.filter(id=menu_id)
            
            if not menu:
                return None, CustomMassenergizeError("Menu not found")
            
            menu = menu.first()
            
            default_menus = load_default_menus_from_json()
            
            menu.content = default_menus["PortalMainNavLinks"]
            # menu.footer_content = default_menus["PortalFooterQuickLinks"]
            # menu.contact_info = default_menus["PortalFooterContactInfo"]
            menu.is_custom = False
            menu.save()
            
            return menu, None
        except Exception as e:
            return None, CustomMassenergizeError(str(e))
        
        
        
    def list_all_languages(self, context, args) -> (dict, Exception):
        """ Get all the languages """
        try:
            all_languages = load_json("database/raw_data/other/languages.json")
            return all_languages, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))
