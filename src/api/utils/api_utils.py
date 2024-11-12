from datetime import datetime
import secrets
import string
from math import atan2, cos, radians, sin, sqrt

from django.utils.text import slugify
from _main_.utils.constants import COMMUNITY_URL_ROOT, DEFAULT_SOURCE_LANGUAGE_CODE
from _main_.utils.utils import load_json
from apps__campaigns.models import CallToAction, Section
from database.models import AboutUsPageSettings, ActionsPageSettings, Community, CommunityAdminGroup, \
    ContactUsPageSettings, DonatePageSettings, EventsPageSettings, ImpactPageSettings, Media, SupportedLanguage, \
    TeamsPageSettings, TestimonialsPageSettings, TranslationsCache, UserProfile, VendorsPageSettings


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


def generate_random_key(name, key_length=10):
    """
    Generate a random key of specified length with an associated name,
    and return them as a single string in the format 'name-key'.

    :param name: The name to associate with the key.
    :param key_length: Length of the random key. Default is 10.
    :return: A string in the format 'name-key'.
    """
    
    alphabet = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(alphabet) for _ in range(key_length))
    
    if not name:
        return key.lower()
    
    return f"{name}-{key}".lower()

# -------------------------- Menu Utils --------------------------


def has_no_custom_website(community, host):
    if host and host == COMMUNITY_URL_ROOT:
        return True
    
    elif community.community_website and community.community_website.first() and community.community_website.first().website:
        return False
    
    return True


def prepend_prefix_to_links(menu_item, prefix):
  
    if not menu_item:
        return None
    if "link" in menu_item:
        existing_link = menu_item["link"]
        
        if existing_link.startswith("/"):
            existing_link = existing_link[1:]
        if not existing_link.startswith(("http", "https")):
            menu_item["link"] = f"{prefix}/{existing_link}"
        
    if "children" in menu_item:
        
        for child in menu_item["children"]:
            prepend_prefix_to_links(child, prefix)
            
    return menu_item


def modify_menu_items_if_published(menu_items, page_settings):
    def process_items(items):
        active_menu_items = []
        for item in items:
            if not item.get("children"):
                name = item.get("link", "").strip("/")
                
                if name in page_settings:
                    active_menu_items.append({**item,"is_published": page_settings[name]})
            
            else:
                if item.get("name") == "Home":
                    active_menu_items.append(item)
                else:
                    item["children"] = process_items(item["children"])
                    if item["children"]:
                        active_menu_items.append(item)
                        
        return active_menu_items
    
    if not menu_items or not page_settings:
        return []
    
    processed_menu_items = process_items(menu_items)
    
    return processed_menu_items


def get_viable_menu_items(community):
    about_us_page_settings = AboutUsPageSettings.objects.filter(community=community).first()
    events_page_settings = EventsPageSettings.objects.filter(community=community).first()
    impact_page_settings = ImpactPageSettings.objects.filter(community=community).first()
    actions_page_settings = ActionsPageSettings.objects.filter(community=community).first()
    contact_us_page_settings = ContactUsPageSettings.objects.filter(community=community).first()
    teams_page_settings = TeamsPageSettings.objects.filter(community=community).first()
    testimonial_page_settings = TestimonialsPageSettings.objects.filter(community=community).first()
    vendors_page_settings = VendorsPageSettings.objects.filter(community=community).first()
    donate_page_settings = DonatePageSettings.objects.filter(community=community).first()

    all_menu = load_json("database/raw_data/portal/menu.json")

    nav_menu = all_menu.get("PortalMainNavLinks")
    
    portal_main_nav_links = modify_menu_items_if_published(nav_menu, {
        "impact": impact_page_settings.is_published if impact_page_settings else True,
        "aboutus": about_us_page_settings.is_published if about_us_page_settings else True,
        "contactus": contact_us_page_settings.is_published if contact_us_page_settings else True,
        "actions": actions_page_settings.is_published if actions_page_settings else True,
        "services": vendors_page_settings.is_published if vendors_page_settings else True,
        "testimonials": testimonial_page_settings.is_published if testimonial_page_settings else True,
        "teams": teams_page_settings.is_published if teams_page_settings else True,
        "events": events_page_settings.is_published if events_page_settings else True,
        "donate": donate_page_settings.is_published if donate_page_settings else True,
    })
    
    footer_menu_content = all_menu.get('PortalFooterQuickLinks')

    portal_footer_contact_info = all_menu.get('PortalFooterContactInfo')
    return {
        "PortalMainNavLinks": portal_main_nav_links,
        "PortalFooterQuickLinks": footer_menu_content,
        "PortalFooterContactInfo": portal_footer_contact_info
    }
# -------------------------- Menu Utils --------------------------


def load_default_menus_from_json(json_file_path=None):
    if not json_file_path:
        json_file_path = "database/raw_data/portal/menu.json"
        
    json = load_json(json_file_path)
    
    return json


def validate_menu_content(content):
    
    if not content or not isinstance(content, list):
        return False
    
    for item in content:
        if not item.get('name', None):
            return False
        
        if not item.get('link', None) and not item.get('children', None):
            return False
        
        if item.get('children', None):
            
            if not validate_menu_content(item['children']):
                
                return False
    return True


def prepare_menu_items_for_portal(content, prefix):
        if not content:
            return None

        prepared_menu_items = []
        
        for item in content:
            prepared_menu_item = prepend_prefix_to_links(item, prefix)
            prepared_menu_items.append(prepared_menu_item)
            
        return prepared_menu_items


def remove_unpublished_menu_items(content, links_to_hide=[]):
    if not content:
        return None

    published_items = []
    
    for item in content:
        if not item.get("children"):
            if item.get("is_published") and item.get("link") not in links_to_hide:
                published_items.append(item)
        else:
            if not item.get("is_published"):
                continue
            item["children"] = remove_unpublished_menu_items(item["children"], links_to_hide)
            if item["children"]:
                published_items.append(item)
            
    return published_items


def get_list_of_internal_links(is_footer=False):
    """
    Returns a list of internal links
    """
    try:
        default_menu = load_default_menus_from_json()
        if not default_menu:
            return None, "Could not load default menus."
        if is_footer:
            menu = default_menu.get("PortalFooterQuickLinks", {})
            menu = menu.get("links", [])
        else:
            menu = default_menu.get("PortalMainNavLinks", [])
           
        
        internal_links = []
        for item in menu:
            if item.get("children"):
                for child in item["children"]:
                    internal_links.append({"name": child.get("name"), "link": child.get("link")})
            else:
                internal_links.append({"name": item.get("name"), "link": item.get("link")})
        
        return internal_links, None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, str(e)


def get_translation_from_cache(text_hash, target_language):
    translation = TranslationsCache.objects.filter(hash__hash=text_hash, target_language_code=target_language).first()
    return translation.translated_text if translation else None


def get_supported_language(language_code):
    supported_language = SupportedLanguage.objects.filter(code=language_code).first()
    if supported_language:
        return supported_language.code
    return DEFAULT_SOURCE_LANGUAGE_CODE


def create_or_update_call_to_action_from_dict(cta_dict):
    if not cta_dict or not isinstance(cta_dict, dict):
        return None
    cta_id = cta_dict.get("id", None)
    
    cta, _ = CallToAction.objects.update_or_create(
        id=cta_id,
        defaults={
            "text": cta_dict.get("text", ""),
            "url": cta_dict.get("url", ""),
        }
    )

    return cta


def create_or_update_section_from_dict(section_dict, media=None):
    if not section_dict or not isinstance(section_dict, dict):
        return None
    section_id = section_dict.get("id", None)
    call_to_action_items = section_dict.get("call_to_action_items", [])
    
    defaults = {
        "title": section_dict.get("title", ""),
        "description": section_dict.get("description", ""),
    }
    if not is_null(media):
        defaults["media"] = create_media_file(media, f"section-{section_dict.get('title','')}")
    section, _ = Section.objects.update_or_create(
        id=section_id,
        defaults=defaults
    )
    
    if call_to_action_items:
        for cta_dict in call_to_action_items:
            cta = create_or_update_call_to_action_from_dict(cta_dict)
            if cta:
                section.call_to_action_items.add(cta)

    return section


def create_unique_slug(title, model, field_name="slug", prefix=None):
    """
    Create a unique slug for a model instance based on the title.

    :param title: The title to base the slug on.
    :param model: The model class to check for existing slugs.
    :param field_name: The field name to check for uniqueness. Default is "slug".
    :param prefix: An optional prefix to add to the slug.
    :return: A unique slug string.
    """
    if not title:
        return None

    slug = slugify(title)
    if not model or not field_name:
        return slug.lower() if not prefix else f"{prefix}-{slug}".lower()
    
    slug = f"{prefix}-{slug}".lower() if prefix else slug.lower()

    if not model.objects.filter(**{field_name: slug}).exists():
        return slug.lower() if not prefix else f"{prefix}-{slug}".lower()
        
    timestamp = str(int(datetime.now().timestamp()))
    
    return  f"{slug}-{timestamp}".lower()


    
