
from _main_.utils.common import serialize, serialize_all
from apps__campaigns.models import  Campaign, CampaignCommunity, CampaignConfiguration, CampaignEvent, CampaignFollow, CampaignLink, CampaignManager, CampaignPartner, CampaignTechnology, CampaignTechnologyLike, CampaignTechnologyTestimonial, CampaignTechnologyView, Comment, Technology, TechnologyCoach, TechnologyOverview, TechnologyVendor
from database.utils.common import get_json_if_not_none
from django.db.models import Count





def get_campaign_details(campaign_id, for_campaign=False, email=None):
    techs = CampaignTechnology.objects.filter(campaign__id=campaign_id, is_deleted=False)
    ser_techs = serialize_all(techs, full=True)
    prepared = [{"campaign_technology_id":x.get("id"),**get_campaign_technology_details(x.get("id"), for_campaign,email )} for x in ser_techs]
    managers = CampaignManager.objects.filter(campaign_id=campaign_id, is_deleted=False)
    partners = CampaignPartner.objects.filter(campaign_id=campaign_id, is_deleted=False)
    communities = CampaignCommunity.objects.filter(campaign_id=campaign_id, is_deleted=False)
    config = CampaignConfiguration.objects.filter(campaign__id=campaign_id, is_deleted=False).first()
    key_contact = CampaignManager.objects.filter(campaign__id=campaign_id, is_deleted=False, is_key_contact=True).first()
    campaign_views = CampaignTechnologyView.objects.filter(campaign_technology__campaign__id=campaign_id, is_deleted=False).first()
    
    if email:
        my_testimonials = CampaignTechnologyTestimonial.objects.filter(is_deleted=False,campaign_technology__campaign__id=campaign_id, created_by__email=email).order_by("-created_at")
#  find a way to add comments here without making it too slow
    return {
        "key_contact": {
            "name": key_contact.user.full_name,
            "email": key_contact.user.email,
            "phone_number": key_contact.contact,
            "image": get_json_if_not_none(key_contact.user.profile_picture),
        } if key_contact else None,

        "my_testimonials": serialize_all(my_testimonials[:5]) if email else [],
        "campaign_views":campaign_views.count if campaign_views else 0,
        "technologies": prepared,
        "communities": serialize_all(communities),
        "managers": serialize_all(managers),
        "partners": serialize_all(partners),
        "config": serialize(config),
        "navigation": generate_campaign_navigation(campaign_id),
    }


def get_campaign_technology_details(campaign_technology_id, campaign_home, email=None):
    campaign_tech = CampaignTechnology.objects.filter(id=campaign_technology_id).first()
    events = CampaignEvent.objects.filter(event__technology__id=campaign_tech.technology.id, is_deleted=False)
    testimonials = CampaignTechnologyTestimonial.objects.filter(is_deleted=False,campaign_technology__id=campaign_technology_id).order_by("-created_at")
    tech_data = get_technology_details(campaign_tech.technology.id)
    comments = Comment.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False).order_by("-created_at")[:20]

    if campaign_home:
        return {
            "testimonials":serialize_all(testimonials[:3]),
            "events": serialize_all(events[:3], full=True),
            "coaches": tech_data.get("coaches", [])[:3],
            "campaign_id": campaign_tech.campaign.id,
            "comments": serialize_all(comments),
            **campaign_tech.technology.simple_json()
        }
    campaign_technology_views = CampaignTechnologyView.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False).first()
    likes = CampaignTechnologyLike.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False).first()

    return {
            **get_technology_details(campaign_tech.technology.id),
            "campaign_technology_views":campaign_technology_views.count if campaign_technology_views else 0,
            "likes":likes.count if likes else 0,
            "testimonials":serialize_all(testimonials),
            "comments": serialize_all(comments),
            "events": serialize_all(events, full=True),
            "campaign_id": campaign_tech.campaign.id,
            "campaign_technology_id": campaign_technology_id,
        }



def get_technology_details(technology_id):
    tech = Technology.objects.filter(id=technology_id).first()
    coaches = TechnologyCoach.objects.filter(technology_id=technology_id, is_deleted=False)
    incentives = TechnologyOverview.objects.filter(technology_id=technology_id, is_deleted=False)
    vendors = TechnologyVendor.objects.filter(technology_id=technology_id, is_deleted=False)

    
    data = {
              "coaches": serialize_all(coaches),
            "overview": serialize_all(incentives),
            "vendors": serialize_all(vendors),
            **serialize(tech),
    }
    return data

def generate_campaign_navigation(campaign_id):
    home_route = f"/{campaign_id}"
    BASE_NAVIGATION = [
        {"key": "home", "url": home_route, "text": "Home", "icon": "fa-home"},
        {"key": "Communities", "url": f"{home_route}/?section=communities", "text": "Communities", "icon": "fa-globe"},
        # {"key": "contact-us", "url": "#", "text": "Contact Us", "icon": "fa-phone"},
    ]

    MENU = [
        {"key": "coaches", "url": f"{home_route}/?section=coaches", "text": "Coaches", "icon": "fa-users", "children": []},
        {"key": "vendors", "url": f"{home_route}/?section=vendors", "text": "Vendors", "children": [], "icon": "fa-handshake-o"},
        {"key": "testimonial", "url": f"{home_route}/?section=testimonial", "text": "Testimonials", "children": [], "icon": "fa-comment"},
        {"key": "events", "url": f"{home_route}/?section=events", "text": "Events", "children": [], "icon": "fa-calendar"},
        {"key": "incentives", "url": f"{home_route}/?section=incentives", "text": "Incentives", "children": [], "icon": "fa-money"},
    ]

    campaign_techs = CampaignTechnology.objects.filter(campaign__id=campaign_id, is_deleted=False)

    for tech in campaign_techs:
        tech_details = get_campaign_technology_details(tech.id, False)
        for index, category in enumerate(["coaches", "vendors", "testimonials", "events"]):
            if tech_details.get(category):
                MENU[index]["children"].append(
                    {"key": tech.id, "url": f"/campaign/{campaign_id}/technology/{tech.id}/?section={category}", "text": tech.technology.name}
                )
        deal_section = tech.deal_section or {}

        if deal_section.get("title"):
            MENU[-1]["children"].append( {"key": tech.id, "url": f"/campaign/{campaign_id}/technology/{tech.id}/?section=incentives", "text": tech.technology.name})

    MENU = [item for item in MENU if item["children"]]  # Remove items without children
    return [*BASE_NAVIGATION, *MENU]



def generate_analytics_data(campaign_id):
    #  number of likes, number of views, number of followers, number of comments, number of testimonials,
    
    utm_medium_counts = (
        CampaignLink.objects.filter(is_deleted=False, campaign__id=campaign_id)
        .values("utm_medium")
        .annotate(count=Count("utm_medium"))
        .order_by("utm_medium")
    )
    likes = (
        CampaignTechnologyLike.objects.filter(
            is_deleted=False, campaign_technology__campaign__id=campaign_id
        )
        .values("campaign_technology__technology__name")
        .annotate(count=Count("campaign_technology__technology"))
        .order_by("campaign_technology__technology")
    )
    views = (
        CampaignTechnologyView.objects.filter( is_deleted=False, campaign_technology__campaign__id=campaign_id)
        .values("campaign_technology__technology__name")
        .annotate(count=Count("campaign_technology__technology"))
        .order_by("campaign_technology__technology")
    )
    followers = (CampaignFollow.objects.filter(is_deleted=False, campaign__id=campaign_id)
        .values("community")
        .annotate(count=Count("community"))
        .order_by("community")
    )
    comments = (
        Comment.objects.filter(is_deleted=False, campaign_technology__campaign__id=campaign_id)
        .values("campaign_technology__technology__name")
        .annotate(count=Count("campaign_technology__technology"))
        .order_by("campaign_technology__technology")
    )
    testimonials = ( CampaignTechnologyTestimonial.objects.filter( is_deleted=False, campaign_technology__campaign__id=campaign_id)
        .values("campaign_technology__technology__name")
        .annotate(count=Count("campaign_technology__technology"))
        .order_by("campaign_technology__technology")
    )

    stats = {
        "shares": list(utm_medium_counts),
        "likes": [
            {
                "technology": entry.get(
                    "campaign_technology__technology__name"
                ),
                "count": entry.get("count"),
            }
            for entry in list(likes)
        ],
        "views": [
            {
                "technology": entry.get(
                    "campaign_technology__technology__name"
                ),
                "count": entry.get("count"),
            }
            for entry in list(views)
        ],
        "followers": [
            {"community": entry.get("community"), "count": entry.get("count")}
            for entry in list(followers)
        ],
        "comments": [
            {
                "technology": entry.get(
                    "campaign_technology__technology__name"
                ),
                "count": entry.get("count"),
            }
            for entry in list(comments)
        ],
        "testimonials": [
            {
                "technology": entry.get(
                    "campaign_technology__technology__name"
                ),
                "count": entry.get("count"),
            }
            for entry in list(testimonials)
        ],
    }
    return stats





def copy_campaign_data(template, new_campaign):
    # copy events, technologies, managers, partners,technology overview, technology coach, technology vendors to new campaign
    # copy campaign configuration to new campaign


    # copy technologies
    campaign_techs = CampaignTechnology.objects.filter(campaign__id=template.id, is_deleted=False)
    for tech in campaign_techs:
        tech.id = None
        tech.campaign = new_campaign
        tech.save()

    # copy events
    campaign_events = CampaignEvent.objects.filter(campaign__id=template.id, is_deleted=False)
    for event in campaign_events:
        event.id = None
        event.campaign = new_campaign
        event.save()
    
    # copy managers
    campaign_managers = CampaignManager.objects.filter(campaign__id=template.id, is_deleted=False)
    for manager in campaign_managers:
        manager.id = None
        manager.campaign = new_campaign
        manager.save()
    
    # copy partners
    campaign_partners = CampaignPartner.objects.filter(campaign__id=template.id, is_deleted=False)
    for partner in campaign_partners:
        partner.id = None
        partner.campaign = new_campaign
        partner.save()

        
    




