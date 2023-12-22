import os
from django.core.files import File
from apps__campaigns.constants import (
    COACHES_SECTION,
    COMMUNITIES_SECTION,
    DEALS_SECTION,
    MORE_INFO_SECTION,
    VENDORS_SECTION,
)
from apps__campaigns.models import (
    Campaign,
    CampaignCommunity,
    CampaignConfiguration,
    CampaignTechnologyEvent,
    CampaignManager,
    CampaignPartner,
    CampaignTechnology,
    CampaignTechnologyTestimonial,
    CampaignTechnologyView,
    Partner,
    Technology,
    TechnologyCoach,
    TechnologyOverview,
    TechnologyVendor,
)
from database.models import Community, Event, Media, UserProfile, Vendor


def create_media(image_path):
    media = Media()
    with open(os.path.join(os.path.dirname(__file__), image_path), "rb") as img_file:
        media.file.save(os.path.basename(image_path), File(img_file), save=True)
        media.name = f"Test media for {image_path}"
    return media


def create_test_users():
    users = []
    arr = [
        {
            "full_name": "John Doe",
            "email": "john.doe@me.org",
            "profile_picture": create_media("media/face2.jpeg"),
        },
        {
            "full_name": "Jane Doe",
            "email": "jane.doe@me.org",
            "profile_picture": create_media("media/face1.jpeg"),
        },
        {
            "full_name": "Kane Doe",
            "email": "kane.doe@me.org",
            "profile_picture": create_media("media/face2.jpeg"),
        },
    ]

    for item in arr:
        user, _ = UserProfile.objects.get_or_create(
            email=item["email"], full_name=item["full_name"]
        )
        users.append(user)

    return users


def get_3_communities():
    arr = ["Community 1", "Community 2", "Community 3"]
    imgs = ["media/solar-panel.jpg", "media/me-biom.png", "media/me-round-logo.png"]
    comm = []
    for item in arr:
        media = create_media(imgs[arr.index(item)])
        community, _ = Community.objects.get_or_create(
            name=item, subdomain=item.lower().replace(" ", "-")
        )
        if _:
            community.logo = media
            community.save()
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
        },
        {
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
        },
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

    vendors = Vendor.objects.filter(is_deleted=False, is_published=True).order_by("-created_at")[:3]
    for vendor in vendors:
        tech_vendor = TechnologyVendor()
        tech_vendor.technology = technology
        tech_vendor.vendor = vendor
        tech_vendor.save()


def create_technology(name, image=None):
    technology = Technology()
    technology.name = name
    technology.description = f"This is a template technology description for {name}"
    technology.image = image
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
            "title": f"This is a testimonial for {campaign_tech.technology.name} 1",
            "description": "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image": create_media("media/food.jpeg"),
            "created_by": user1,
            "community": comm,
            "is_approved": True,
            "is_published": True,
        },
        {
            "title": f"This is a testimonial for {campaign_tech.technology.name}",
            "description": "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image": create_media("media/climate2.jpeg"),
            "created_by": user2,
            "community": comm2,
            "is_approved": True,
            "is_published": True,
        },
        {
            "title": f"This is a testimonial for {campaign_tech.technology.name}",
            "description": "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image": create_media("media/climate2.jpeg"),
            "created_by": user3,
            "community": comm3,
            "is_approved": True,
            "is_published": True,
        },
    ]

    for item in arr:
        campaign_technology_view = CampaignTechnologyTestimonial()
        campaign_technology_view.campaign_technology = campaign_tech
        campaign_technology_view.title = item["title"]
        campaign_technology_view.body = item["description"]
        campaign_technology_view.image = item["image"]
        campaign_technology_view.created_by = item["created_by"]
        campaign_technology_view.community = item["community"]
        campaign_technology_view.is_approved = item["is_approved"]
        campaign_technology_view.is_published = item["is_published"]

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


def create_campaign_configuration(campaign):
    print("====== Creating Campaign Configuration ======")

    # create campaign configuration
    campaign_configuration = CampaignConfiguration()
    campaign_configuration.campaign = campaign
    campaign_configuration.advert = {
        "title": "What is Kicking Gas?",
        "description": "Kicking Gas helps residents of South Whidbey  migrate from oil, propane, or wood to electric.",
        "link": "https://www.google.com",
    }
    campaign_configuration.save()


def create_campaign_communities(campaign):
    print("====== Creating Campaign Communities ======")
    comm, comm2, comm3 = get_3_communities()
    link = "https://docs.google.com/spreadsheets/d/1wQ4858rQippxNqZ5c_kD985P_XOza9PW/edit#gid=676780580"
    # bulk create
    campaign_communities = CampaignCommunity.objects.bulk_create(
        [
            CampaignCommunity(campaign=campaign, community=comm, help_link=link),
            CampaignCommunity(campaign=campaign, community=comm2, help_link=link),
            CampaignCommunity(campaign=campaign, community=comm3, help_link=link),
        ]
    )
    return campaign_communities


def create_template_campaign():
    primary_logo = create_media("media/me-biom.png")
    secondary_logo = create_media("media/me-round-logo.png")
    image = create_media("media/campaign_image.jpg")

    campaign = Campaign(
        title="Template Campaign",
        description="This is a template campaign description",
        primary_logo=primary_logo,
        secondary_logo=secondary_logo,
        image=image,
        is_template=True,
        tagline="This a template campaign tagline",
        communities_section=COMMUNITIES_SECTION,
    )

    campaign.save()

    print("====== created Template Campaign ======")
    # create campaign managers
    create_campaign_Managers(campaign)
    # create campaign partners
    create_campaign_partners(campaign)

    # create communities
    create_campaign_communities(campaign)

    # create campaign config
    create_campaign_configuration(campaign)

    return campaign


def create_campaign_event(campaign_tech):
    print("====== Creating Campaign Events ======")
    com1, com2, com3 = get_3_communities()
    events = [
        {
            "name": "New Event 1",
            "description": "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image": create_media("media/climate2.jpeg"),
            "start_date_and_time": "2024-09-01 00:00:00",
            "end_date_and_time": "2024-09-03 00:00:00",
            "community": com1,
        },
        {
            "name": "New Event 2",
            "description": "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image": create_media("media/climate3.jpeg"),
            "start_date_and_time": "2024-09-01 00:00:00",
            "end_date_and_time": "2024-09-03 00:00:00",
            "community": com2,
        },
        {
            "name": "New Event 3",
            "description": "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "image": create_media("media/ev1.jpeg"),
            "start_date_and_time": "2024-09-01 00:00:00",
            "end_date_and_time": "2024-09-03 00:00:00",
            "community": com3,
        },
    ]

    for event in events:
        evn, _ = Event.objects.get_or_create(**event)
        campaign_event = CampaignTechnologyEvent()
        campaign_event.campaign_technology = campaign_tech
        campaign_event.event = evn
        campaign_event.save()


def create_template_campaign_technology(campaign_id):
    print("====== Creating Template Campaign Technologies ======")
    techs = []
    campaign = Campaign.objects.filter(id=campaign_id).first()
    techs = [
        {"name": "Heat Pump", "image": create_media("media/pump.jpeg")},
        {"name": "Solar Community", "image": create_media("media/com-solar.png")},
        {"name": "Home Solar", "image": create_media("media/solar-panel.jpg")},
    ]

    for tech in techs:
        technology = create_technology(tech["name"], tech["image"])
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
