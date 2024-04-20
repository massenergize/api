from datetime import datetime,timedelta
from math import atan2, cos, radians, sin, sqrt

from django.db.models import Q

from _main_.utils.common import serialize_all
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagConstants
from database.models import AboutUsPageSettings, Action, ActionsPageSettings, Community, CommunityAdminGroup, \
    ContactUsPageSettings, Event, EventsPageSettings, FeatureFlag, ImpactPageSettings, Media, Menu, \
    Policy, TagCollection, Team, TeamsPageSettings, Testimonial, TestimonialsPageSettings, UserProfile, \
    Vendor, VendorsPageSettings
from database.utils.settings.admin_settings import AdminPortalSettings
from database.utils.settings.user_settings import UserPortalSettings


def is_admin_of_community(context, community_id):
    # super admins are admins of any community
    if context.user_is_super_admin:
        return True
    if not context.user_is_community_admin:
        return False

    user_id = context.user_id
    user_email = context.user_email
    if not community_id:
        return False
    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
    else:
        user = UserProfile.objects.filter(email=user_email).first()
    community_admins = CommunityAdminGroup.objects.filter(
        community__id=community_id
    ).first()
    if not community_admins:
        return False
    is_admin = community_admins.members.filter(id=user.id).exists()
    return is_admin


def get_user_community_ids(context):
    user_id = context.user_id
    user_email = context.user_email
    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
    else:
        user = UserProfile.objects.filter(email=user_email).first()
    if not user:
        return None
    ids = user.communityadmingroup_set.all().values_list("community__id", flat=True)
    return list(ids)


def get_key(name):
    arr = name.lower().split(" ")
    return "-".join(arr) + "-template-id"


def get_distance_between_coords(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    difference_long = lon2 - lon1
    difference_lat = lat2 - lat1

    a = (
        sin(difference_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(difference_long / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def is_null(val):
    if val in ["", None, [], {}, "undefined", "null"]:
        return True
    return False


def get_sender_email(community_id):
    DEFAULT_SENDER = "no-reply@massenergize.org"
    if not community_id:
        return DEFAULT_SENDER
    community = Community.objects.filter(id=community_id).first()
    if not community:
        return DEFAULT_SENDER
    postmark_info = community.contact_info if community.contact_info else {}
    if not community.owner_email:
        return DEFAULT_SENDER

    if postmark_info.get("is_validated"):
        return community.owner_email

    return DEFAULT_SENDER


def create_media_file(file, name):
    if not file:
        return None
    if file == "reset":
        return None
    media = Media.objects.create(name=name, file=file)
    media.save()
    return media


class DonationPageSettings:
    pass

def prependPrefixToLinks(menu_item, prefix):
    if not menu_item:
        return None
    if "link" in menu_item:
        menu_item["link"] = "/" + prefix + menu_item["link"]
    if "children" in menu_item:
        for child in menu_item["children"]:
            prependPrefixToLinks(child, prefix)
    return menu_item

def modify_menu_items_if_published(menu_items, page_settings, prefix):
    if not menu_items or not page_settings or not prefix:
        return []
    
    main_menu = []
    
    for item in menu_items:
        if not item.get("children"):
            name = item.get("link", "").strip("/")
            if name in page_settings and not page_settings[name]:
                main_menu.remove(item)
        else:
            for child in item["children"]:
                name = child.get("link", "").strip("/")
                if name in page_settings and not page_settings[name]:
                    item["children"].remove(child)
        
    for item in menu_items:
        f = prependPrefixToLinks(item,prefix)
        main_menu.append(f)

    return main_menu

def get_viable_menu_items(community):

    about_us_page_settings = AboutUsPageSettings.objects.filter(community=community).first()
    events_page_settings = EventsPageSettings.objects.filter(community=community).first()
    impact_page_settings = ImpactPageSettings.objects.filter(community=community).first()
    actions_page_settings = ActionsPageSettings.objects.filter(community=community).first()
    contact_us_page_settings = ContactUsPageSettings.objects.filter(community=community).first()
    teams_page_settings = TeamsPageSettings.objects.filter(community=community).first()
    testimonial_page_settings = TestimonialsPageSettings.objects.filter(community=community).first()
    vendors_page_settings = VendorsPageSettings.objects.filter(community=community).first()

    menu_items = {}
    all_menu = Menu.objects.all()

    nav_menu = all_menu.get(name="PortalMainNavLinks")
    
    portal_main_nav_links = modify_menu_items_if_published(nav_menu.content, {
        "impact": impact_page_settings.is_published,
        "aboutus": about_us_page_settings.is_published,
        "contactus": contact_us_page_settings.is_published,
        "actions": actions_page_settings.is_published,
        "services": vendors_page_settings.is_published,
        "testimonials": testimonial_page_settings.is_published,
        "teams": teams_page_settings.is_published,
        "events": events_page_settings.is_published
    }, community.subdomain)
    
    footer_menu_content = all_menu.get(name='PortalFooterQuickLinks')
    
    portal_footer_quick_links = [
        {**item, "link": "/"+community.subdomain + "/" + item["link"]}
        if not item.get("children") and item.get("navItemId", None) != "footer-report-a-bug-id"
        else item
        for item in footer_menu_content.content["links"]
    ]
    portal_footer_contact_info = all_menu.get(name='PortalFooterContactInfo')
    return [
        {**nav_menu.simple_json(), "content": portal_main_nav_links},
        {**footer_menu_content.simple_json(), "content": {"links": portal_footer_quick_links}},
        portal_footer_contact_info.simple_json()
        
    ]
    
# .......................... site setup utils ..........................
def get_enabled_feature_flags_for_community(community):
    feature_flags =  FeatureFlag.objects.filter(
                Q(audience=FeatureFlagConstants().for_everyone()) |
                Q(audience=FeatureFlagConstants().for_specific_audience(), communities=community) |
                (Q(audience=FeatureFlagConstants().for_all_except()) & ~Q(communities=community))
            ).exclude(expires_on__lt=datetime.now()).prefetch_related('communities')
    
    return feature_flags
def get_actions_for_community(community, context):
    actions = Action.objects.select_related('image', 'community').prefetch_related('tags', 'vendors').filter(community=community)
    if not context.is_sandbox:
        if context.user_is_logged_in and not context.user_is_admin():
            actions = actions.filter(Q(user__id=context.user_id) | Q(is_published=True))
        else:
            actions = actions.filter(is_published=True)
    return actions.distinct()


def get_events_for_community(community, context):
    today = datetime.now()
    shared_months = 2
    hosted_months = 6
    earliest_shared = today - timedelta(weeks=4 * shared_months)
    earliest_hosted = today - timedelta(weeks=4 * hosted_months)
    
    events = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(
        community__id=community.id, start_date_and_time__gte=earliest_hosted)
    
    shared = community.events_from_others.filter(is_published=True, start_date_and_time__gte=earliest_shared)
    if not context.is_sandbox and events:
        if context.user_is_logged_in and not context.user_is_admin():
            events = events.filter(Q(user__id=context.user_id) | Q(is_published=True))
        else:
            events = events.filter(is_published=True)
    all_events = [*events, *shared]
    
    return all_events


def get_teams_for_community(community):
    pass

def get_testimonials_for_community(community, context):
    
    testimonials = Testimonial.objects.filter(
        community=community, is_deleted=False).prefetch_related('tags__tag_collection', 'action__tags', 'vendor',
                                                                'community')
    
    if not context.is_sandbox:
        if context.user_is_logged_in and not context.user_is_admin():
            testimonials = testimonials.filter(Q(user__id=context.user_id) | Q(is_published=True))
        else:
            testimonials = testimonials.filter(is_published=True)
        
    return testimonials.distinct()

def get_vendors_for_community(community, context):
    vendors = community.community_vendors.filter(is_deleted=False)
    
    if not context.is_sandbox:
        if context.user_is_logged_in and not context.user_is_admin():
            vendors = vendors.filter(Q(user__id=context.user_id) | Q(is_published=True))
        else:
            vendors = vendors.filter(is_published=True)
    return vendors.distinct()

def get_tags_collections():
    return TagCollection.objects.filter(is_deleted=False)

# .......................... site setup utils ..........................
def load_homepage_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["home_page_settings"].simple_json() if page_settings["home_page_settings"] else None
    data["feature_flags"] = serialize_all(get_enabled_feature_flags_for_community(community))
    data["impact_page_settings"] = page_settings["impact_page_settings"].simple_json() if page_settings["impact_page_settings"] else None
    return data

def load_actions_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["actions_page_settings"].simple_json() if page_settings["actions_page_settings"] else None
    data["actions"] = serialize_all(get_actions_for_community(community, context))
    data["tag_collections"] = serialize_all(get_tags_collections())
    return data

def load_events_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["events_page_settings"].simple_json() if page_settings["events_page_settings"] else None
    data["events"] = serialize_all(get_events_for_community(community, context))
    data["tag_collections"] = serialize_all(get_tags_collections())
    return data

def load_vendors_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["vendors_page_settings"].simple_json() if page_settings["vendors_page_settings"] else None
    data["vendors"] = serialize_all(get_vendors_for_community(community, context))
    data["tag_collections"] = serialize_all(get_tags_collections())
    return data

def load_about_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["about_us_page_settings"].simple_json() if page_settings["about_us_page_settings"] else None
    data["donate_page_settings"] = {}
    return data

def load_testimonials_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["testimonials_page_settings"].simple_json() if page_settings["testimonials_page_settings"] else None
    data["testimonials"] = serialize_all(get_testimonials_for_community(community, context))
    data["tag_collections"] = serialize_all(get_tags_collections())
    return data

def load_one_vendor_data(context, args, community, id, page_settings):
    data = {}
    vendor = Vendor.objects.filter(id=id).first()
    data["vendor"] = vendor.simple_json()
    data["testimonials"] = serialize_all(Testimonial.objects.filter(vendor=vendor))
    return data

def load_impact_data(context, args, community, id, page_settings):
    from api.store.graph import GraphStore
    data = {}
    completed_action_graph_data, err = GraphStore().graph_actions_completed(context, args)
    communities_impact_graph, _ = GraphStore().graph_communities_impact(context, args)
    data["tag_collections"] = serialize_all(get_tags_collections())
    data["graph_actions_completed"] = completed_action_graph_data
    data["graph_communities_impact"] = communities_impact_graph
    return data

def load_aboutus_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["about_us_page_settings"].simple_json() if page_settings["about_us_page_settings"] else None
    return data

def load_contactus_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["contact_us_page_settings"].simple_json() if page_settings["contact_us_page_settings"] else None
    return data

def load_teams_data(context, args, community, id, page_settings):
    from api.store.team import TeamStore
    from api.store.graph import GraphStore
    data = {}
    completed_action_graph_data, err = GraphStore().graph_actions_completed(context, args)
    teams_stats, _ = TeamStore().team_stats(context, args)
    data["page_data"] = page_settings["teams_page_settings"].simple_json() if page_settings["teams_page_settings"] else None
    data["graph_actions_completed"] = completed_action_graph_data
    data["teams_stats"] = teams_stats
    return data

def load_one_team_data(context, args, community, id, page_settings):
    from api.store.team import TeamStore
    data = {}
    teams_stats, _ = TeamStore().team_stats(context, args)
    data["team"] = Team.objects.filter(id=id).first().simple_json()
    data["teams_stats"] = teams_stats
    return data

def load_one_action_data(context, args, community, id, page_settings):
    from api.store.graph import GraphStore
    data = {}
    completed_action_graph_data, err = GraphStore().graph_actions_completed(context, args)
    data["graph_actions_completed"] = completed_action_graph_data
    data["action"] = Action.objects.filter(id=id).first().simple_json()
    return data

def load_one_event_data(context, args, community, id, page_settings):
    data = {}
    data["page_data"] = page_settings["events_page_settings"].simple_json() if page_settings["events_page_settings"] else None
    data["event"] = Event.objects.filter(id=id).first().simple_json()
    return data

def load_one_testimonial_data(context, args, community, id, page_settings):
    data = {}
    data["testimonial"] = Testimonial.objects.filter(id=id).first().simple_json()
    return data

def load_profile_data(context, args, community, id, page_settings):
    from api.store.team import TeamStore
    data = {}
    teams_stats, _ = TeamStore().team_stats(context, args)
    data["teams_stats"] = teams_stats
    return data

def load_settings_data(context, args, community, id, page_settings):
    data = {}
    if context.user_is_admin():
        data["preferences"] = UserPortalSettings.Preferences if args.get("subdomain") else AdminPortalSettings.Preferences
    else:
        data["preferences"] = UserPortalSettings.Preferences
    return data

def load_policies_data(context, args, community, id, page_settings):
    data = {}
    policies = Policy.objects.filter(is_deleted=False)
    data["policies"] = policies
    return data

