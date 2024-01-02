
from _main_.utils.common import serialize, serialize_all

from apps__campaigns.models import  CampaignAccount, CampaignAccountAdmin, CampaignCommunity, CampaignConfiguration, CampaignEvent, CampaignFollow, CampaignLink, CampaignManager, CampaignPartner, CampaignTechnology, CampaignTechnologyLike, CampaignTechnologyTestimonial, CampaignTechnologyView, CampaignView, Comment, Technology, TechnologyCoach, TechnologyOverview, TechnologyVendor

# from database.models import Event
from database.utils.common import get_json_if_not_none
from django.db.models import Count, Sum



def get_user_accounts(user):
    # get all the campaigns the user is a manager of
    manager_of = CampaignAccountAdmin.objects.filter(user=user, is_deleted=False)
    created = CampaignAccount.objects.filter(creator=user, is_deleted=False)
    campaign_accounts = list(set(created) | set([a.account for a in manager_of]))
    return [ca.simple_json() for ca in campaign_accounts]


def create_new_event(ct):
    from apps__campaigns.create_campaign_template import create_campaign_event
    evs = create_campaign_event(ct)
    return evs
    



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
    events = CampaignEvent.objects.filter(technology_event__technology__id=campaign_tech.technology.id, is_deleted=False)
    testimonials = CampaignTechnologyTestimonial.objects.filter(is_deleted=False,campaign_technology__id=campaign_technology_id, is_approved=True,is_published=True).order_by("-created_at")
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
    home_route = f"/campaign/{campaign_id}"
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
    
    shares =CampaignLink.objects.filter(is_deleted=False, campaign__id=campaign_id).count()
    likes = CampaignTechnologyLike.objects.filter(campaign_technology__campaign__id=campaign_id, is_deleted=False).aggregate(total_likes=Sum('count'))['total_likes']
    campaign_technology_views = CampaignTechnologyView.objects.filter(campaign_technology__campaign__id=campaign_id,is_deleted=False).aggregate(total_views=Sum('count'))['total_views']
    followers = CampaignFollow.objects.filter(is_deleted=False, campaign__id=campaign_id).count()
    comments =Comment.objects.filter(is_deleted=False, campaign_technology__campaign__id=campaign_id).count()
    testimonials =CampaignTechnologyTestimonial.objects.filter( is_deleted=False, campaign_technology__campaign__id=campaign_id).count()
    campaign_views = CampaignView.objects.filter(campaign__id=campaign_id, is_deleted=False).aggregate(total_views=Sum('count'))['total_views']
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




def select_3_random_events_from_communities(community_ids):
    from database.models import Event
    from random import sample
    events = Event.objects.filter(is_deleted=False, community__id__in=community_ids, is_published=True).order_by("-start_date_and_time")
    count = events.count()

    if count > 3:
        return sample(list(events), 3)
    else:
        return list(events)




# def copy_campaign_data(template, new_campaign):
#     campaign_techs = CampaignTechnology.objects.filter(campaign__id=template.id, is_deleted=False)
#     campaign_events = list(template.campaign_event.all())
#     communities= [x.community for x in template.campaign_community.all()]

#     for campaign_tech in campaign_techs:
#         tech  = campaign_tech.technology

#         overviews = list(tech.technology_overview.all())
#         coaches = list(tech.technology_coach.all())
#         vendors = list(tech.technology_vendor.all())
#         testimonials = list(campaign_tech.campaign_technology_testimonials.all())
    

#         tech.id = None
#         tech.save()

#         campaign_tech.id = None
#         campaign_tech.campaign = new_campaign
#         campaign_tech.technology = tech
#         campaign_tech.save()

#         for overview in overviews:
#             overview.pk = None
#             overview.technology = tech
#             overview.save()

#         for coach in coaches:
#             coach.pk = None
#             coach.technology = tech
#             coach.save()

#         for vendor in vendors:
#             vendor.pk = None
#             vendor.technology = tech
#             vendor.save()


#         # copy testimonials
#         for testimonial in testimonials:
#             testimonial.pk = None
#             testimonial.campaign_technology = campaign_tech
#             testimonial.save()


    
#     for tech in list(new_campaign.campaign_technology_campaign.all()):
#         try:
#             create_new_event(tech)

#         except Exception as e:
#             print("Error creating CampaignEvent:", e)




#     # copy managers
#     campaign_managers = CampaignManager.objects.filter(campaign__id=template.id, is_deleted=False)
#     for manager in campaign_managers:
#         try:
#             manager.id = None
#             manager.campaign = new_campaign
#             manager.save()
#         except Exception as e:
#             print("Error creating CampaignManager:", e)

#     # copy partners
#     campaign_partners = CampaignPartner.objects.filter(campaign__id=template.id, is_deleted=False)
#     for partner in campaign_partners:
#         try:
#             partner.id = None
#             partner.campaign = new_campaign
#             partner.save()
#         except Exception as e:
#             print("Error creating CampaignPartner:", e)


#     # copy config
#     campaign_config = CampaignConfiguration.objects.filter(campaign__id=template.id, is_deleted=False).first()
#     if campaign_config:
#         campaign_config.id = None
#         campaign_config.campaign = new_campaign
#         campaign_config.save()

        
    
def copy_campaign_data(template, new_campaign):

    # copy technologies
    campaign_techs = CampaignTechnology.objects.filter(campaign__id=template.id, is_deleted=False)
    for tech in campaign_techs:
        testimonials = list(tech.campaign_technology_testimonials.filter(is_deleted=False))

        tech.id = None
        tech.campaign = new_campaign
        tech.save()


        # copy testimonials
        for testimonial in testimonials:
            testimonial.pk = None
            testimonial.campaign_technology = tech
            testimonial.save() 


    
    # copy managers
    campaign_managers = CampaignManager.objects.filter(campaign__id=template.id, is_deleted=False)
    for manager in campaign_managers:
        manager.id = None
        manager.campaign = new_campaign
        manager.save()
    
    # # copy partners
    # campaign_partners = CampaignPartner.objects.filter(campaign__id=template.id, is_deleted=False)
    # for partner in campaign_partners:
    #     partner.id = None
    #     partner.campaign = new_campaign
    #     partner.save()

    #     # copy config
    campaign_config = CampaignConfiguration.objects.filter(campaign__id=template.id, is_deleted=False).first()
    if campaign_config:
        campaign_config.id = None
        campaign_config.campaign = new_campaign
        campaign_config.save()



