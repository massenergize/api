import os
from django.core.files import File
from apps__campaigns.constants import COACHES_SECTION, DEALS_SECTION, MORE_INFO_SECTION, VENDORS_SECTION
from apps__campaigns.models import Campaign, CampaignEvent, CampaignManager, CampaignPartner, CampaignTechnology, CampaignTechnologyTestimonial, CampaignTechnologyView, Partner, Technology, TechnologyCoach, TechnologyOverview, TechnologyVendor
from database.models import Community, Event, Media, UserProfile, Vendor

def create_media(image_path):
    media = Media()
    with open(os.path.join(os.path.dirname(__file__), image_path), 'rb') as img_file:
        media.file.save(os.path.basename(image_path), File(img_file), save=True)
        media.name = f"Test media for {image_path}"
    return media



def create_test_users():
    users = []
    arr = [
        {
            "full_name": "John Doe",
            "email": "john.doe@me.org",
        },{
            "full_name": "Jane Doe",
            "email": "jane.doe@me.org",
        },
        {
            "full_name": "Kane Doe",
            "email": "kane.doe@me.org",
        }
        ]
    
    for item in arr:
        user, _ = UserProfile.objects.get_or_create(email=item["email"], full_name=item["full_name"])
        users.append(user)

    return users
    
def get_3_communities():
    arr = ["Community 1", "Community 2", "Community 3"]
    comm = []
    for item in arr:
        community, _ = Community.objects.get_or_create(name=item, subdomain=item.lower().replace(" ", "-"))
        comm.append(community)
    return comm

def create_campaign_technology_overview(technology_id):
    tech = Technology.objects.filter(id=technology_id, is_deleted=False).first()
    arr = [
        {
            "title": "ENVIRONMENTALLY FRIENDLY",
            "image": create_media("media/solar-panel.jpg"),
            "description": "1500s, when an unknown printer took a galley of type rised in the 1960s with the release of L1500s, when an unknown printer took a galley of type rised in the 1960s with the release of",
        },
        {
            "title": "ECONOMIC BENEFITS",
            "image": create_media("media/solar-panel.jpg"),
            "description": "1500s, when an unknown printer took a galley of type rised in the 1960s with the release of L1500s, when an unknown printer took a galley of type rised in the 1960s with the release of",
        },
        {
            "title": "HEALTH & WELLNESS",
            "image": create_media("media/solar-panel.jpg"),
            "description": "1500s, when an unknown printer took a galley of type rised in the 1960s with the release of L1500s, when an unknown printer took a galley of type rised in the 1960s with the release of",
        },
    ]

    for item in arr:
        campaign_technology_overview = TechnologyOverview()
        campaign_technology_overview.technology = tech
        campaign_technology_overview.title = item["title"]
        campaign_technology_overview.description = item["description"]
        campaign_technology_overview.image = item["image"]
        campaign_technology_overview.save()



def create_technology_coaches(technology_id):
    technology = Technology.objects.filter(id=technology_id, is_deleted=False).first()
    arr = [
        {
            "full_name": "John Doe",
            "email": "john.doe@me.org",
            "phone_number": "1234567890",
            "image": create_media("media/face2.jpeg"),
        },{
            "full_name": "Jane Doe",
            "email": "jane.doe@me.org",
            "phone_number": "1234567890",
            "image": create_media("media/face1.jpeg"),
        },
        {
            "full_name": "Kane Doe",
            "email": "kane.doe@me.org",
            "phone_number": "1234567890",
            "image": create_media("media/face6.jpeg"),
        }
        ]
    
    for item in arr:
        coach = TechnologyCoach()
        coach.technology = technology
        coach.full_name = item["full_name"]
        coach.email = item["email"]
        coach.phone_number = item["phone_number"]
        coach.image = item["image"]
        coach.save()


def create_technology_vendors(technology_id):
    technology = Technology.objects.filter(id=technology_id, is_deleted=False).first()

    vendors = Vendor.objects.filter(is_deleted=False,is_published=True).order_by("-created_at")[:10]
    for vendor in vendors:
        tech_vendor = TechnologyVendor()
        tech_vendor.technology = technology
        tech_vendor.vendor = vendor
        tech_vendor.save()





def create_technology(name, icon_name=None):
    technology = Technology()
    technology.name = name
    technology.description = f"This is a template technology description for {name}"
    technology.icon = icon_name
    technology.save()

    # create overview
    create_campaign_technology_overview(technology.id)

    # create coaches
    create_technology_coaches(technology.id)


    # create vendors
    create_technology_vendors(technology.id)


    return technology


def create_campaign_technology_testimonial(campaign_technology_id):
    print("====== Creating Campaign Technology Testimonials ======")
    campaign_tech = CampaignTechnology.objects.filter(id=campaign_technology_id).first()

    user1, user2, user3 = create_test_users()
    comm, comm2, comm3 = get_3_communities()
    arr = [
        {
            "title": "This is a testimonial title 1",
            "description": "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image": create_media("media/food.jpeg"),
            "created_by": user1,
            "community":comm
        },
        {
            "title": "This is a testimonial title 2",
            "description": "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image": create_media("media/climate2.jpeg"),
            "created_by": user2,
            "community":comm2

        }
    ]

    for item in arr:
        campaign_technology_view = CampaignTechnologyTestimonial()
        campaign_technology_view.campaign_technology = campaign_tech
        campaign_technology_view.title = item["title"]
        campaign_technology_view.body = item["description"]
        campaign_technology_view.image = item["image"]
        campaign_technology_view.created_by = item["created_by"]
        campaign_technology_view.community = item["community"]
        campaign_technology_view.save()



def create_campaign_partners(campaign):
    print("====== Creating Campaign Partners ======")
    arr = [
        {
            "name": "Partner 1",
            "website": "https://www.google.com",
            "logo": create_media("media/google.png"),
            "phone_number": "1234567890",
            "email": "parner1@gmail.com",
        },
        {
            "name": "Partner 2",
            "website": "https://www.google.com",
            "logo": create_media("media/plastic.png"),
            "phone_number": "1234567890",
            "email": "parner2@gmail.com",
        },
        {
            "name": "Partner 3",
            "website": "https://www.google.com",
            "logo": create_media("media/leaders.jpg"),
            "phone_number": "1234567890",
            "email": "parner3@gmail.com",
        },
        {
            "name": "Partner 4",
            "website": "https://www.google.com",
            "logo": create_media("media/me-round-logo.png"),
            "phone_number": "1234567890",
            "email": "parner4@gmail.com",
        },
    ]


    for item in arr:
        partner, _ = Partner.objects.get_or_create(**item)
        campaign_partner = CampaignPartner()
        campaign_partner.campaign = campaign
        campaign_partner.partner = partner
        campaign_partner.save()


def create_campaign_Managers(campaign):
    print("====== Creating Campaign Managers ======")
    user1, user2, user3 = create_test_users()
    users = [
        {
            "user": user1,
            "is_key_contact": True,
            "contact": "1234567890",
        },
        {
            "user": user2,
            "is_key_contact": False,
            "contact": "1234567890",
        },
        {
            "user": user3,
            "is_key_contact": False,
            "contact": "1234567890",
        },
    ]
    for user in users:
        campaign_manager = CampaignManager()
        campaign_manager.campaign = campaign
        campaign_manager.user = user["user"]
        campaign_manager.is_key_contact = user["is_key_contact"]
        campaign_manager.contact = user["contact"]
        campaign_manager.save()
         


def create_template_campaign():
    primary_logo = create_media("media/me-biom.png")
    secondary_logo = create_media("media/me-round-logo.png")
    image = create_media("media/campaign_image.jpg")

    campaign = Campaign()
    campaign.title = "Template Campaign"
    campaign.description = "This is a template campaign description"
    campaign.primary_logo = primary_logo
    campaign.secondary_logo = secondary_logo
    campaign.image = image
    campaign.is_template = True
    campaign.tagline = "This a template campaign tagline"
    campaign.start_date = "2024-09-01"
    campaign.save()

    print("====== created Template Campaign ======")
    # create campaign managers
    create_campaign_Managers(campaign)
    # create campaign partners
    create_campaign_partners(campaign)

    return campaign

def create_campaign_event(campaign_tech):
    print("====== Creating Campaign Events ======")
    com1, com2, com3 = get_3_communities()
    events = [
        {
            "name":"New Event 1",
            "description":"lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image":create_media("media/climate2.jpeg"),
            "technology":campaign_tech.technology,
            "start_date_and_time":"2024-09-01 00:00:00",
            "end_date_and_time":"2024-09-03 00:00:00",
            "community":com1,            
        },
        {
            "name":"New Event 2",
            "description":"lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image":create_media("media/climate3.jpeg"),
            "technology":campaign_tech.technology,
            "start_date_and_time":"2024-09-01 00:00:00",
            "end_date_and_time":"2024-09-03 00:00:00",
            "community":com2,

        },
        {
            "name":"New Event 3",
            "description":"lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image":create_media("media/ev1.jpeg"),
            "technology":campaign_tech.technology,
            "start_date_and_time":"2024-09-01 00:00:00",
            "end_date_and_time":"2024-09-03 00:00:00",
            "community":com3,

        }
    ]


    for event in events:
        evn, _ = Event.objects.get_or_create(**event)
        campaign_event = CampaignEvent()
        campaign_event.campaign = campaign_tech.campaign
        campaign_event.event = evn
        campaign_event.save()




def create_template_campaign_technology(campaign_id):
    print("====== Creating Template Campaign Technologies ======")
    techs = []
    campaign = Campaign.objects.filter(id=campaign_id).first()
    techs = [
        {"name": "Heat Pump", "icon_name": "heat-pump"},
        {"name": "Solar Community", "icon_name": "fa-solar-panel"},
        {"name": "Home Solar", "icon_name": "fa-sun"},
    ]

    for tech in techs:
        technology = create_technology(tech["name"], tech["icon_name"])
        campaign_technology = CampaignTechnology()
        campaign_technology.campaign = campaign
        campaign_technology.technology = technology

        campaign_technology.coaches_section = COACHES_SECTION
        campaign_technology.vendors_section = VENDORS_SECTION
        campaign_technology.deal_section = DEALS_SECTION
        campaign_technology.more_info_section = MORE_INFO_SECTION
        campaign_technology.overview_title = f"Why Choose {technology.name}?"
        campaign_technology.action_section = {}

        campaign_technology.save()

        # create accessories

        create_campaign_technology_testimonial(campaign_technology.id)
        create_campaign_event(campaign_technology)
  


# main function
def run():
    print("==== Creating Template Campaign ====")
    does_template_exist = Campaign.objects.filter(is_template=True).first()
    if does_template_exist:
        print("Template Campaign Already Exists")
        return
    campaign = create_template_campaign()

    create_template_campaign_technology(campaign.id)
    print("Template Campaign Created Successfully !!!")
    return