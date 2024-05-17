from math import atan2, cos, radians, sin, sqrt
from database.models import AboutUsPageSettings, ActionsPageSettings, Community, CommunityAdminGroup, \
    ContactUsPageSettings, EventsPageSettings, ImpactPageSettings, Media, Menu, \
    TeamsPageSettings, TestimonialsPageSettings, UserProfile, \
    VendorsPageSettings
import pyshorteners


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

# -------------------------- Menu Utils --------------------------


def prepend_prefix_to_links(menu_item: object, prefix: object) -> object:
    if not menu_item:
        return None
    if "link" in menu_item:
        existing_link = menu_item["link"]
        if existing_link.startswith("/"):
            existing_link = existing_link[1:]
        menu_item["link"] = f"/{prefix}/{existing_link}"
    if "children" in menu_item:
        for child in menu_item["children"]:
            prepend_prefix_to_links(child, prefix)
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
        f = prepend_prefix_to_links(item, prefix)
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
        "events": events_page_settings.is_published,
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
# -------------------------- Menu Utils --------------------------
