import os
from random import random
from django.core.files import File
from apps__campaigns.constants import (
    COACHES_SECTION,
    COMMUNITIES_SECTION,
    DEALS_SECTION,
    MORE_INFO_SECTION,
    NAME_DESCRIPTION,
    VENDORS_SECTION,
)
from apps__campaigns.models import (
    Campaign,
    CampaignCommunity,
    CampaignConfiguration,
    CampaignEvent,
    CampaignManager,
    CampaignPartner,
    CampaignTechnology,
    CampaignTechnologyTestimonial,
    Partner,
    Technology,
    TechnologyCoach,
    TechnologyEvent,
    TechnologyOverview,
    TechnologyVendor,
)
from database.models import Community, Event, Media, Testimonial, UserProfile, Vendor


TEMPLATE_TITLE = "Template Campaign 1"


def create_media(image_path):
    try:
        media = Media()
        with open(os.path.join(os.path.dirname(__file__), image_path), "rb") as img_file:
            media.file.save(os.path.basename(image_path), File(img_file), save=True)
            media.name = f"Test media for {image_path}"
        return media
    except Exception as e:
        print(f"Error creating media: {str(e)}")
        return None


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
    try:
        arr = ["Community 1", "Community 2", "Community 3"]
        imgs = ["media/solar-panel.jpg", "media/me-biom.png", "media/me-round-logo.png"]
        comm = []
        for item in arr:
            media = create_media(imgs[arr.index(item)])
            community, _ = Community.objects.get_or_create(name=item, subdomain=item.lower().replace(" ", "-"))
            if _:
                community.logo = media
                community.save()
            comm.append(community)
        return comm
    except Exception as e:
        print(f"Error creating communities: {str(e)}")
        return []


def create_campaign_technology_overview(technology_id):
    try:
        tech = Technology.objects.filter(id=technology_id, is_deleted=False).first()
        arr = [
            {
                "title": "ENVIRONMENTALLY FRIENDLY",
                "image": create_media("media/solar-panel.jpg"),
                "description": f"{tech.name} is a renewable energy source that is environmentally friendly and sustainable. It is a clean source of energy that does not emit greenhouse gases when used to generate electricity. It is a renewable source of energy, which means that it will not run out like other sources of energy such as fossil fuels.",
            },
            {
                "title": "ECONOMIC BENEFITS",
                "image": create_media("media/climate3.jpeg"),
                "description": f"{tech.name} is a renewable energy source that has economic benefits. It is a clean source of energy that does not emit greenhouse gases when used to generate electricity. It is a renewable source of energy, which means that it will not run out like other sources of energy such as fossil fuels.",
            },
            {
                "title": "HEALTH & WELLNESS",
                "image": create_media("media/climate2.jpeg"),
                "description": "{tech.name} is a renewable energy source that has health and wellness benefits. It is a clean source of energy that does not emit greenhouse gases when used to generate electricity. It is a renewable source of energy, which means that it will not run out like other sources of energy such as fossil fuels.",
            },
        ]

        for item in arr:
            campaign_technology_overview = TechnologyOverview()
            campaign_technology_overview.technology = tech
            campaign_technology_overview.title = item["title"]
            campaign_technology_overview.description = item["description"]
            campaign_technology_overview.image = item["image"]
            campaign_technology_overview.save()
    except Exception as e:
        print(f"Error creating campaign technology overview: {str(e)}")


def create_technology_coaches(technology_id):
    try:
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
    except Exception as e:
        print(f"Error creating technology coaches: {str(e)}")


def create_technology_vendors(technology_id):
    try:
        technology = Technology.objects.filter(id=technology_id, is_deleted=False).first()

        vendors = Vendor.objects.filter(is_deleted=False, is_published=True).order_by("-created_at")[:3]
        for vendor in vendors:
            tech_vendor = TechnologyVendor()
            tech_vendor.technology = technology
            tech_vendor.vendor = vendor
            tech_vendor.save()
    except Exception as e:
        print(f"Error creating technology vendors: {str(e)}")


def create_technology_events(tech):
    try:
        print("====== Creating Technology Events ======")
        com1, com2, com3 = get_3_communities()

        name1, description1 = NAME_DESCRIPTION[int(random() * len(NAME_DESCRIPTION))].values()
        name2, description2 = NAME_DESCRIPTION[int(random() * len(NAME_DESCRIPTION))].values()
        name3, description3 = NAME_DESCRIPTION[int(random() * len(NAME_DESCRIPTION))].values()


        events = [
            {
                "name": name1,
                "description": description1,
                "image": create_media("media/climate2.jpeg"),
                "start_date_and_time": "2024-09-01 00:00:00",
                "end_date_and_time": "2024-09-03 00:00:00",
                "community": com1,
                "external_link": "https://communities.massenergize.org/",
            },
            {
                "name": name2,
                "description": description2,
                "image": create_media("media/climate3.jpeg"),
                "start_date_and_time": "2024-09-01 00:00:00",
                "end_date_and_time": "2024-09-03 00:00:00",
                "community": com2,
                "external_link": "https://community.massenergize.org/Massachusetts",
            },
            {
                "name": name3,
                "description": description3,
                "image": create_media("media/ev1.jpeg"),
                "start_date_and_time": "2024-09-01 00:00:00",
                "end_date_and_time": "2024-09-03 00:00:00",
                "community": com3,
                "external_link": "https://community.massenergize.org/EcoNatick",
            },
        ]

        for event in events:
            evn, _ = Event.objects.get_or_create(**event)
            campaign_event = TechnologyEvent()
            campaign_event.technology = tech
            campaign_event.event = evn
            campaign_event.save()
    except Exception as e:
        print(f"Error creating technology events: {str(e)}")



def create_technology(name, image=None, description=None):
    try:
        technology = Technology()
        technology.name = name
        technology.description = description
        technology.image = image
        technology.save()

        # create overview
        create_campaign_technology_overview(technology.id)

        # create coaches
        create_technology_coaches(technology.id)

        # create vendors
        create_technology_vendors(technology.id)


        # add technology events
        create_technology_events(technology)

        return technology
    except Exception as e:
        print(f"Error creating technology: {str(e)}")


def create_campaign_technology_testimonial(campaign_technology_id):
    try:
        print("====== Creating Campaign Technology Testimonials ======")
        campaign_tech = CampaignTechnology.objects.filter(id=campaign_technology_id).first()

        user1, user2, user3 = create_test_users()
        comm, comm2, comm3 = get_3_communities()
        # get random title and description

        title1, description1 = NAME_DESCRIPTION[int(random() * len(NAME_DESCRIPTION))].values()
        title2, description2 = NAME_DESCRIPTION[int(random() * len(NAME_DESCRIPTION))].values()
        title3, description3 = NAME_DESCRIPTION[int(random() * len(NAME_DESCRIPTION))].values()

        arr = [
            {
                "title": title1,
                "description": description1,
                "image": create_media("media/food.jpeg"),
                "created_by": user1,
                "community": comm,
                "is_approved": True,
                "is_published": True,
            },
            {
                "title": title2,
                "description":description2 ,
                "image": create_media("media/climate2.jpeg"),
                "created_by": user2,
                "community": comm2,
                "is_approved": True,
                "is_published": True,
            },
            {
                "title":title3,
                "description": description3,
                "image": create_media("media/climate2.jpeg"),
                "created_by": user3,
                "community": comm3,
                "is_approved": True,
                "is_published": True,
            },
        ]

        for item in arr:
            testimonial = Testimonial()
            testimonial.title = item["title"]
            testimonial.body = item["description"]
            testimonial.image = item["image"]
            testimonial.user = item["created_by"]
            testimonial.community = item["community"]
            testimonial.is_approved = item["is_approved"]
            testimonial.is_published = item["is_published"]
            testimonial.save()


            campaign_technology_view = CampaignTechnologyTestimonial()
            campaign_technology_view.campaign_technology = campaign_tech
            campaign_technology_view.testimonial =testimonial

            campaign_technology_view.save()
    except Exception as e:
        print(f"An error occurred while creating testimonials: {str(e)}")


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
    try:
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
    except Exception as e:
        print(f"An error occurred while creating campaign managers: {str(e)}")


def create_campaign_configuration(campaign):
    print("====== Creating Campaign Configuration ======")

    # create campaign configuration
    campaign_configuration = CampaignConfiguration()
    campaign_configuration.campaign = campaign
    campaign_configuration.advert = {
        "title": "What is Kicking Gas?",
        "description": "In the vast expanse of the cosmos, where stars twinkle like ancient storytellers, humanity embarks on a perpetual journey of exploration and discovery. It is a journey fueled by insatiable curiosity, a desire to unravel the mysteries woven into the fabric of the universe. From the towering peaks of scientific inquiry to the tranquil valleys of artistic expression, each step forward is a testament to the indomitable human spirit. As we navigate the intricate dance of celestial bodies, scientists meticulously parse the cosmic code, decoding the language of quasars and galaxies. Simultaneously, artists, inspired by the cosmos' ethereal beauty, capture the essence of interstellar wonders on canvases that become portals to otherworldly realms. This exploration is not confined to the celestial; it extends to the depths of our oceans, where marine biologists unravel the secrets of life teeming in the abyss. It traverses the uncharted territories of the mind, where philosophers contemplate the profound questions that echo across time. It is a journey that transcends the boundaries of disciplines, inviting all to partake in the collective endeavor to understand, appreciate, and cherish the boundless wonders that await us on this cosmic odyssey.",
        "link": "https://www.google.com",
    }
    campaign_configuration.save()


def create_campaign_communities(campaign):
    print("====== Creating Campaign Communities ======")
    comm, comm2, comm3 = get_3_communities()
    # bulk create
    campaign_communities = CampaignCommunity.objects.bulk_create(
        [
            CampaignCommunity(campaign=campaign, community=comm, help_link="https://docs.google.com/forms/d/1iEodwBtlDcvtZH-dS0--AkJpJn5aHUzhfrZExxKUzm8/edit"),
            CampaignCommunity(campaign=campaign, community=comm2, help_link="https://docs.google.com/forms/d/1Kh-jfVIzjErbWyh2QA6n4By14Tuqbk7qkBek8_Al2S4/edit"),
            CampaignCommunity(campaign=campaign, community=comm3, help_link="https://docs.google.com/forms/d/1uGLuE48R1dq6fAPTluLBdp7tkbOtMl22kxXFyy8ixuM/edit"),
        ]
    )
    return campaign_communities



def create_campaign_events(campaign):
    try:
        techs = CampaignTechnology.objects.filter(campaign=campaign, is_deleted=False)
        for tech in techs:
            events  = TechnologyEvent.objects.filter(technology=tech.technology, is_deleted=False)[:3]
            for event in events:
                campaign_event = CampaignEvent()
                campaign_event.campaign = campaign
                campaign_event.technology_event = event
                campaign_event.save()
    except Exception as e:
        print(f"An error occurred while creating campaign events: {str(e)}")



def create_template_campaign():
    try:
        primary_logo = create_media("media/me-round-logo.png")
        secondary_logo = create_media("media/me-biom.png" )
        image = create_media("media/campaign_image.jpg")

        campaign = Campaign(
            title=TEMPLATE_TITLE,
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
        # create_campaign_partners(campaign)

        # create communities
        create_campaign_communities(campaign)

        # create campaign config
        create_campaign_configuration(campaign)




        return campaign
    except Exception as e:
        print(f"An error occurred while creating template campaign: {str(e)}")
        return None



def create_template_campaign_technology(campaign_id):
    try:
        print("====== Creating Template Campaign Technologies ======")
        techs = []
        campaign = Campaign.objects.filter(id=campaign_id).first()
        techs = [
            {"name": "Heat Pump", "image": create_media("media/pump.jpeg"), "description": "Heat pumps offer an energy-efficient alternative to furnaces and air conditioners for all climates. Like your refrigerator, heat pumps use electricity to transfer heat from a cool space to a warm space, making the cool space cooler and the warm space warmer. During the heating season, heat pumps move heat from the cool outdoors into your warm house.  During the cooling season, heat pumps move heat from your house into the  outdoors. Because they transfer heat rather than generate heat, heat pumps can efficiently provide comfortable temperatures for your home. "},
            {"name": "Solar Community", "image": create_media("media/com-solar.png"), "description": "The U.S. Department of Energy defines community solar as any solar project or purchasing program, within a geographic area, in which the benefits flow to multiple customers such as individuals, businesses, nonprofits, and other groups. In most cases, customers benefit from energy generated by solar panels at an off-site array. Community solar customers typically subscribe to—or in some cases own—a portion of the energy generated by a solar array, and receive an electric bill credit for electricity generated by their share of the community solar system. Community solar can be a great option for people who are unable to install solar panels on their roofs because they are renters, can’t afford solar, or because their roofs or electrical systems aren’t suited to solar. "},
            {"name": "Home Solar", "image": create_media("media/solar-panel.jpg"), "description": "Since 2008, hundreds of thousands of solar panels have popped up across the country as an increasing number of Americans choose to power their daily lives with the sun’s energy. Thanks in part to Solar Energy Technologies Office (SETO) investments, the cost of going solar goes down every year. You may be considering the option of adding a solar energy system to your home’s roof or finding another way to harness the sun’s energy. While there’s no one-size-fits-all solar solution, here are some resources that can help you figure out what’s best for you. Consider these questions before you go solar."},
        ]

        for tech in techs:
            technology = create_technology(tech["name"], tech["image"], tech["description"])
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
    except Exception as e:
        print(f"An error occurred while creating template campaign technologies: {str(e)}")



def run():
    try:
        print("==== Creating Template Campaign ====")
        does_template_exist = Campaign.objects.filter(title=TEMPLATE_TITLE,is_template=True).first()
        if does_template_exist:
            print("Template Campaign Already Exists")
            return
        campaign = create_template_campaign()

        create_template_campaign_technology(campaign.id)

        # create campaign events
        create_campaign_events(campaign)
        print("Template Campaign Created Successfully !!!")
        return
    except Exception as e:
        print(f"An error occurred while creating the template campaign: {str(e)}")
