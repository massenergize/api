
from _main_.utils.common import serialize, serialize_all
from apps__campaigns.models import  CampaignCommunity, CampaignConfiguration, CampaignEvent, CampaignManager, CampaignPartner, CampaignTechnology, CampaignTechnologyLike, CampaignTechnologyTestimonial, CampaignTechnologyView, Comment, Technology, TechnologyCoach, TechnologyOverview, TechnologyVendor
from database.utils.common import get_json_if_not_none


def get_campaign_details(campaign_id, for_campaign=False):
    techs = CampaignTechnology.objects.filter(campaign__id=campaign_id, is_deleted=False)
    ser_techs = serialize_all(techs, full=True)
    prepared = [{"campaign_technology":x.get("id"),**get_technology_details(x.get("technology", {}).get("id"), for_campaign)} for x in ser_techs]
    managers = CampaignManager.objects.filter(campaign_id=campaign_id, is_deleted=False)
    partners = CampaignPartner.objects.filter(campaign_id=campaign_id, is_deleted=False)
    communities = CampaignCommunity.objects.filter(campaign_id=campaign_id, is_deleted=False)
    config = CampaignConfiguration.objects.filter(campaign__id=campaign_id, is_deleted=False).first()
    key_contact = CampaignManager.objects.filter(campaign__id=campaign_id, is_deleted=False, is_key_contact=True).first()

    return {
        "key_contact": {
            "name": key_contact.user.full_name,
            "email": key_contact.user.email,
            "phone_number": key_contact.contact,
            "image": get_json_if_not_none(key_contact.user.profile_picture),
        } if key_contact else None,
        
        "technologies": prepared,
        "communities": serialize_all(communities),
        "managers": serialize_all(managers),
        "partners": serialize_all(partners),
        "config": serialize(config) 
    }


def get_technology_details(technology_id, campaign_home, email=None):
    tech = Technology.objects.filter(id=technology_id).first()
    # all incentive, coaches, vendors,
    coaches = TechnologyCoach.objects.filter(technology_id=technology_id, is_deleted=False)
    testimonials = CampaignTechnologyTestimonial.objects.filter(is_deleted=False,campaign_technology__technology__id=technology_id )
    events = CampaignEvent.objects.filter(event__technology__id=technology_id, is_deleted=False)

    if campaign_home:
          return {
            "coaches": serialize_all(coaches),
            "testimonials":serialize_all(testimonials[:3]),
            "events":serialize_all(events[:3], full=True),
            **serialize(tech)
        }

    else:
        comments = Comment.objects.filter(campaign_technology__technology__id=technology_id, is_deleted=False)
        vendors = TechnologyVendor.objects.filter(technology_id=technology_id, is_deleted=False)
        incentives = TechnologyOverview.objects.filter(technology_id=technology_id, is_deleted=False)
        views = CampaignTechnologyView.objects.filter(campaign_technology__technology__id=technology_id, is_deleted=False)
        likes = CampaignTechnologyLike.objects.filter(campaign_technology__technology__id=technology_id, is_deleted=False)
        liked = CampaignTechnologyLike.objects.filter(campaign_technology__technology__id=technology_id, is_deleted=False, email=email).exists()
        return {
            "views":views.count(),
            "has_liked":liked,
            "likes":likes.count(),
            "overview": serialize_all(incentives),
            "coaches": serialize_all(coaches,full=True),
            "vendors": serialize_all(vendors),
            "testimonials":serialize_all(testimonials),
            "comments": serialize_all(comments),
            "events": serialize_all(events, full=True),
            **serialize(tech)
        }
