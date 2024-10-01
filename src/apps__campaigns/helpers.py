import os
from django.core.files import File
from _main_.utils.common import serialize, serialize_all
from api.constants import CAMPAIGN_TEMPLATE_KEYS
from apps__campaigns.models import CampaignAccount, CampaignAccountAdmin, CampaignCommunity, CampaignFollow, CampaignLink, CampaignManager, CampaignTechnology, CampaignTechnologyEvent, \
    CampaignTechnologyLike, CampaignTechnologyTestimonial, CampaignTechnologyView, CampaignView, Comment, Technology, \
    TechnologyCoach, TechnologyDeal, TechnologyOverview, TechnologyVendor

# from database.models import Event
from database.utils.common import get_json_if_not_none
from django.db.models import Sum
import json


def create_media(image_path):
    from database.models import Media
    try:
        media = Media()
        with open(os.path.join(os.path.dirname(__file__), image_path), "rb") as img_file:
            media.file.save(os.path.basename(image_path), File(img_file), save=True)
            media.name = f"Test media for {image_path}"
        return media
    except Exception as e:
        print(f"Error creating media: {str(e)}")
        return None


def get_user_accounts(user):
    # get all the campaigns the user is a manager of
    manager_of = CampaignAccountAdmin.objects.filter(user=user, is_deleted=False)
    created = CampaignAccount.objects.filter(creator=user, is_deleted=False)
    campaign_accounts = list(set(created) | set([a.account for a in manager_of]))
    return [ca.simple_json() for ca in campaign_accounts]



def get_campaign_details(campaign_id, for_campaign=False):
    techs = CampaignTechnology.objects.filter(campaign__id=campaign_id, is_deleted=False)
    prepared = [{"campaign_technology_id": str(x.id), **get_campaign_technology_details({ "campaign_technology_id": str(x.id),"for_admin":True})} for x in techs]
    managers = CampaignManager.objects.filter(campaign_id=campaign_id, is_deleted=False).order_by("-created_at")
    communities = CampaignCommunity.objects.filter(campaign_id=campaign_id, is_deleted=False)
    
    communities = sorted(communities, key=lambda x:  x.alias or x.community.name)
    return {
        "technologies": prepared,
        "communities": serialize_all(communities),
        "managers": serialize_all(managers),
    }


def get_campaign_technology_details(args):
    campaign_technology_id = args.get("campaign_technology_id")
    campaign_home = args.get("campaign_home")
    for_admin = args.get("for_admin", False)

    campaign_tech = CampaignTechnology.objects.get(id=campaign_technology_id)
    events = CampaignTechnologyEvent.objects.filter(campaign_technology=campaign_tech, is_deleted=False).select_related("campaign_technology").order_by("event__start_date_and_time")
    coaches = TechnologyCoach.objects.filter(technology_id=campaign_tech.technology.id, is_deleted=False)
    comments = Comment.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False).order_by("-created_at")[:20]
    if for_admin:
        testimonials = CampaignTechnologyTestimonial.objects.filter(is_deleted=False,campaign_technology__id=campaign_technology_id)
    else:
        testimonials = CampaignTechnologyTestimonial.objects.filter(is_deleted=False,campaign_technology__id=campaign_technology_id, testimonial__is_published=True)
     
    if campaign_home:
        data =  {
            "testimonials": serialize_all(testimonials.filter(is_featured=True)),
            "events": serialize_all(events, full=True),
            "coaches": serialize_all(coaches),
            "campaign_id": campaign_tech.campaign.id,
        }
        if campaign_tech.campaign.template_key != CAMPAIGN_TEMPLATE_KEYS.get("MULTI_TECHNOLOGY_CAMPAIGN"):
            data = {**data, **get_technology_details(campaign_tech.technology.id)}
        else:
            data = {**data, **serialize(campaign_tech.technology)}
            
        return data
    campaign_technology_views = CampaignTechnologyView.objects.filter(campaign_technology__id=campaign_technology_id,is_deleted=False).first()
    likes = CampaignTechnologyLike.objects.filter(campaign_technology__id=campaign_technology_id,is_deleted=False).first()

    return {
        **get_technology_details(campaign_tech.technology.id, True),
        "campaign_technology_views": campaign_technology_views.count if campaign_technology_views else 0,
        "likes": likes.count if likes else 0,
        "testimonials": serialize_all(testimonials),
        "comments": serialize_all(comments),
        "events": serialize_all(events, full=True),
        "campaign_id": campaign_tech.campaign.id,
        "campaign_technology_id": campaign_technology_id,
    }


def get_technology_details(technology_id, for_campaign=False):
    tech = Technology.objects.get(id=technology_id)
    coaches = tech.technology_coach.filter(is_deleted=False)
    incentives = tech.technology_overview.filter(is_deleted=False)
    vendors = TechnologyVendor.objects.filter(technology__id=technology_id, is_deleted=False).order_by("vendor__name")
    deals = tech.technology_deal.filter(is_deleted=False)
    technology_actions = tech.technology_action.filter(is_deleted=False)
    faqs = tech.technology_faq.all()
    

    data = {
        "coaches": serialize_all(coaches),
        "overview": serialize_all(incentives),
        "vendors": serialize_all(vendors),
        "deals": serialize_all(deals),
        "technology_actions": serialize_all(technology_actions),
        "faqs": serialize_all(faqs),
        **serialize(tech),
    }
    return data


def get_campaign_details_for_user(campaign, email):
    techs = CampaignTechnology.objects.filter(campaign__id=campaign.id, is_deleted=False)
    prepared = [{"campaign_technology_id": str(x.id), **get_campaign_technology_details({"email": email, "campaign_home": True, "campaign_technology_id": str(x.id)})} for x in techs]
    communities = CampaignCommunity.objects.filter(campaign__id=campaign.id, is_deleted=False)
    key_contact = CampaignManager.objects.filter(is_key_contact=True, is_deleted=False, campaign__id=campaign.id).first()
    campaign_views = CampaignTechnologyView.objects.filter(campaign_technology__campaign__id=campaign.id,is_deleted=False).first()
    languages = campaign.supported_languages.filter(is_active=True)

    if email:
        my_testimonials = CampaignTechnologyTestimonial.objects.filter(
            campaign_technology__campaign__id=campaign.id, is_deleted=False,
            testimonial__user__email=email).order_by("-created_at")

    return {
        "key_contact": {
            "name": key_contact.user.full_name,
            "email": key_contact.user.email,
            "phone_number": key_contact.contact,
            "image": get_json_if_not_none(key_contact.user.profile_picture),
        } if key_contact else None,
        "my_testimonials": serialize_all(my_testimonials[:5]) if email else [],
        "technologies": prepared,
        "communities": serialize_all(communities),
        "campaign_views": campaign_views.count if campaign_views else 0,
        "navigation": generate_campaign_navigation(campaign),
        "languages": serialize_all(languages),
    }




def category_has_items(category, campaign_technology):
    if category == "coaches":
        return campaign_technology.technology.technology_coach.filter(is_deleted=False).exists()
    elif category == "vendors":
        return campaign_technology.technology.technology_vendor.filter(is_deleted=False).exists()
    elif category == "events":
        return campaign_technology.campaign_technology_event.filter(is_deleted=False).exists()
    elif category == "testimonials":
        return campaign_technology.campaign_technology_testimonials.filter(is_deleted=False).exists()
    elif category == "deals":
        return campaign_technology.technology.technology_deal.filter(is_deleted=False).exists()
    else:
        return False


def generate_campaign_navigation(campaign):
    home_route = f"/campaign/{campaign.slug}"
    mode = "&preview=true" if not campaign.is_published else ""

    BASE_NAVIGATION = [
        {"key": "home", "url": f'{home_route}/?section=home{mode}', "text": "Home", "icon": "fa-home"},
        {"key": "Communities", "url": f"{home_route}/?section=communities{mode}", "text": "Communities", "icon": "fa-globe"},
        {"key": "technologies", "url": f"{home_route}/?section=technologies{mode}", "text": "Technologies","children": [],"icon": "fa-gears"}, # This index is used to add technologies
        # {"key": "contact-us", "url": "#", "text": "Contact Us", "icon": "fa-phone"},
    ]

    MENU = [
        {"key": "coaches", "url": f"{home_route}/?section=coaches{mode}", "text": "Coaches", "icon": "fa-users",
         "children": []},
        {"key": "vendors", "url": f"{home_route}/?section=vendors{mode}", "text": "Vendors", "children": [],
         "icon": "fa-handshake-o"},
        {"key": "testimonial", "url": f"{home_route}/?section=testimonial{mode}", "text": "Testimonials", "children": [],
         "icon": "fa-comment"},
        {"key": "events", "url": f"{home_route}/?section=events{mode}", "text": "Events", "children": [],
         "icon": "fa-calendar"},
        {"key": "deals", "url": f"{home_route}/?section=deals{mode}", "text": "Deals", "children": [],
         "icon": "fa-money"},
    ]

    campaign_techs = CampaignTechnology.objects.filter(campaign__id=campaign.id, is_deleted=False)

    for tech in campaign_techs:
        for index, category in enumerate(["coaches", "vendors", "testimonials", "events"]):
            if category_has_items(category, tech):
                MENU[index]["children"].append(
                    {"key": tech.id, "url": f"/campaign/{campaign.slug}/technology/{tech.id}/?section={category}{mode}",
                     "text": tech.technology.name}
                )
        deal_section = tech.technology.deal_section or {}

        if deal_section.get("title"):
            MENU[-1]["children"].append(
                {"key": tech.id, "url": f"/campaign/{campaign.slug}/technology/{tech.id}/?section=incentives{mode}",
                 "text": tech.technology.name})

        BASE_NAVIGATION[2]["children"].append({
            "key": tech.id,
            "url": f"/campaign/{campaign.slug}/technology/{tech.id}/?section=home{mode}",
            "text": tech.technology.name
    })


    MENU = [item for item in MENU if item["children"]]  # Remove items without children
    # remove technologies without children
    if not BASE_NAVIGATION[2]["children"]:
        BASE_NAVIGATION.pop(2)
    return [*BASE_NAVIGATION, *MENU]


def generate_analytics_data(campaign_id):
    #  number of likes, number of views, number of followers, number of comments, number of testimonials,

    shares = CampaignLink.objects.filter(is_deleted=False, campaign__id=campaign_id).count()
    likes = CampaignTechnologyLike.objects.filter(campaign_technology__campaign__id=campaign_id,
            is_deleted=False).aggregate(
            total_likes=Sum('count'))['total_likes']
    campaign_technology_views = CampaignTechnologyView.objects.filter(campaign_technology__campaign__id=campaign_id,
            is_deleted=False).aggregate(
            total_views=Sum('count'))['total_views']
    followers = CampaignFollow.objects.filter(is_deleted=False, campaign__id=campaign_id).count()
    comments = Comment.objects.filter(is_deleted=False, campaign_technology__campaign__id=campaign_id).count()
    testimonials = CampaignTechnologyTestimonial.objects.filter(is_deleted=False,
                                                                campaign_technology__campaign__id=campaign_id).count()
    campaign_views = CampaignView.objects.filter(campaign__id=campaign_id, is_deleted=False).aggregate(total_views=Sum('count'))[
            'total_views']
    stats = {
        "shares": shares,
        "likes": likes,
        "campaign views": campaign_views,
        "Technology views": campaign_technology_views,
        "followers": followers,
        "comments": comments,
        "testimonials": testimonials,
    }
    return stats


def copy_campaign_data(new_campaign):
    # Load the JSON data from the template file
    with open('apps__campaigns/main_template.json') as f:
        data = json.load(f)
    try:
        _campaign = data.get("campaign")
        new_campaign.image = create_media(_campaign.get("image"))
        new_campaign.primary_logo = create_media(_campaign.get("primary_logo"))
        new_campaign.secondary_logo = create_media(_campaign.get("secondary_logo"))
        new_campaign.description = _campaign.get("description")
        new_campaign.tagline = _campaign.get("tagline")
        new_campaign.communities_section = _campaign.get("communities_section")
        new_campaign.save()
        print("Campaign created")
        
        #  managers
        print("")
        print("Creating managers")
        manager = CampaignManager()
        manager.user = new_campaign.owner
        manager.campaign = new_campaign
        manager.is_key_contact = True
        manager.role = "Creator"
        manager.save()
        print("Manager created")

        # copy technologies

        _technologies = data.get("technologies")

        for _tech in _technologies:
            print("Creating technology", _tech.get("name"))
            tech = Technology()
            tech.name = _tech.get("name")
            tech.description = _tech.get("description")
            tech.summary = _tech.get("summary")
            tech.image = create_media(_tech.get("image"))
            tech.vendors_section = _tech.get("vendors_section")
            tech.coaches_section = _tech.get("coaches_section")
            tech.deal_section = _tech.get("deal_section")
            tech.overview_title = _tech.get("overview_title")
            tech.campaign_account = new_campaign.account
            tech.save()

            _coaches = _tech.get("coaches")
            for _coach in _coaches:
                print("Creating coach", _coach.get("name"))
                coach = TechnologyCoach()
                coach.full_name = _coach.get("name")
                coach.community = _coach.get("community")
                # coach.image = create_media(_coach.get("image"))
                coach.technology = tech
                coach.save()
            print("Coach created")

            _overview = _tech.get("overviews")
            for _overview_item in _overview:
                print("Creating overview", _overview_item.get("title"))
                overview = TechnologyOverview()
                overview.title = _overview_item.get("title")
                overview.description = _overview_item.get("description")
                overview.technology = tech
                overview.save()

            _deals = _tech.get("deals")
            for _deal in _deals:
                print("Creating deal", _deal.get("title"))
                deal = TechnologyDeal()
                deal.title = _deal.get("title")
                deal.description = _deal.get("description")
                deal.technology = tech
                deal.save()

            campaign_tech = CampaignTechnology()
            campaign_tech.campaign = new_campaign
            campaign_tech.technology = tech
            campaign_tech.save()

            print("Technology created")

        print("Cloning  Done !!!")
    except Exception as e:
        print("==== ERROR_CREATING_CAMPAIGN ====", str(e))
        return None, str(e)
