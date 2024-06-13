import random
from django.db import models
from django.forms import model_to_dict

from _main_.utils.base_model import BaseModel
from database.utils.common import get_json_if_not_none, get_summary_info
from database.utils.constants import LONG_STR_LEN, SHORT_STR_LEN
from django.utils.text import slugify

# Create your models here
def generate_rand_between(start=2, end=10):
    length = random.randint(start, start)  # Random length between 2 and 10
    return  random.randint(end**(length-1), end**length - 1)


def get_comm_alias(campaign, community_id):
    com = campaign.campaign_community.filter(community_id=community_id).first()
    return com.alias if com else None

class CampaignAccount(BaseModel):
    '''
    This model represents a campaign account. An account created by a user or a community to
    be used for creating and managing campaigns.\n
    ---- FIELDS ----\n
    name : str -> Name of the account
    subdomain : str -> Subdomain of the account(will be used in the URL)
    creator : UserProfile -> Creator of the account
    community : Community(optional) -> Community that the account belongs to
    '''
    name  = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=SHORT_STR_LEN, unique=True, blank=True, null=True)
    creator = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE, null=True, blank=True)
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"name:  {self.name}"

    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["community"] = get_summary_info(self.community)
        return res
    
    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ("-created_at",)



class CampaignAccountAdmin(BaseModel):
    '''
    This model represents an admin of a campaign account.\n
    ---- FIELDS ----\n
    account : CampaignAccount -> Campaign account
    user : UserProfile -> User
    role : str -> Role of the user
    
    '''
    account = models.ForeignKey(CampaignAccount, on_delete=models.CASCADE)
    user = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE)
    role = models.CharField(blank=True, max_length=255, null=True)


    def __str__(self) -> str:
        return f"{self.user}||{self.role} || {self.account}"
       
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["account"] = get_summary_info(self.account)
        res["user"] = get_summary_info(self.user)
        
        return res

    def full_json(self):
        return self.simple_json()



class CustomCampaignAccountDomain(BaseModel):
    '''
    This model represents a custom domain name for a campaign account.\n
    ---- FIELDS ----\n
    account : CampaignAccount -> Campaign account
    domain_name : str -> Custom domain name
    '''
    account = models.ForeignKey(CampaignAccount, on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=SHORT_STR_LEN, unique=True)

    def __str__(self) -> str:
        return f"{self.account}||{self.domain_name}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["account"] = get_summary_info(self.account)
        return res

    def full_json(self):
        return self.simple_json()


class Campaign(BaseModel):
    """
    This model represents a campaign.\n
    ---- FIELDS ----\n
    account : CampaignAccount -> Campaign account
    title : str -> Title of the campaign
    description : str -> Description of the campaign
    start_date : date -> Start date of the campaign
    end_date : datetime -> End date of the campaign
    logo : Media(optional) -> Logo of the campaign
    is_approved : bool -> Whether the campaign is approved
    is_published : bool -> Whether the campaign is published
    is_global : bool -> Whether the campaign is open for all
    is_template : bool -> Whether the campaign is a template
    owner : UserProfile(optional) -> Owner of the campaign

    """
    account = models.ForeignKey(CampaignAccount, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    primary_logo = models.ForeignKey("database.Media", on_delete=models.CASCADE, null=True, blank=True, related_name="primary_logo")
    secondary_logo = models.ForeignKey("database.Media", on_delete=models.CASCADE, null=True, blank=True, related_name="secondary_logo")
    image = models.ForeignKey("database.Media", on_delete=models.CASCADE, null=True, blank=True, related_name="campaign_image")
    is_approved = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE, null=True, blank=True)
    communities_section = models.JSONField(blank=True, null=True)
    technologies_section = models.JSONField(blank=True, null=True)
    newsletter_section = models.JSONField(blank=True, null=True)
    coaches_section = models.JSONField(blank=True, null=True)
    about_us_title = models.CharField(max_length=255, blank=True, null=True)



    def __str__(self):
        return f"{self.account} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(generate_rand_between(2, 10))
        super(Campaign,self).save(*args, **kwargs)

    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["account"] = get_summary_info(self.account)
        res["primary_logo"] = get_json_if_not_none(self.primary_logo)
        res["secondary_logo"] = get_json_if_not_none(self.secondary_logo)
        res["image"] = get_json_if_not_none(self.image)
        res["campaign_image"] = get_json_if_not_none(self.image)
        res["owner"] = get_summary_info(self.owner)
        res["end_date"] = self.end_date.strftime("%Y-%m-%d") if self.end_date else None

        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "Campaigns"



class CampaignConfiguration(BaseModel):
    """
    This model represents a campaign configuration.\n
    ---- FIELDS ----\n
    campaign : Campaign -> Campaign
    theme : JSONField(optional) -> Theme
    navigation : JSONField(optional) -> Navigation

    navigation{
    "vendors":True,
    "events":True,
    "testimonials":True,
    "incentives":True,
    "contact_us":True,
    "coaches:True
    }
    
    """
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    theme = models.JSONField(blank=True, null=True)


    def __str__(self):
        return f"{self.campaign} - Configuration"

    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "CampaignConfiguration"



class Technology(BaseModel):
    """
    This model represents a technology.\n 
    ---- FIELDS ----\n
    name : str -> Name of the technology
    description : str -> Description of the technology
    image : Media(optional) -> Image of the technology
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    summary = models.CharField(max_length = SHORT_STR_LEN, blank=True, null=True)
    image = models.ForeignKey("database.Media", on_delete=models.CASCADE, null=True, blank=True)
    help_link = models.CharField(max_length=255, blank=True, null=True)
    campaign_account = models.ForeignKey(CampaignAccount, on_delete=models.CASCADE, null=True, blank=True, related_name="campaign_account_technology")
    user = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE, null=True, blank=True, related_name="user_technology")

    overview_title = models.CharField(max_length=255, blank=True, null=True)
    coaches_section = models.JSONField(blank=True, null=True)
    deal_section = models.JSONField(blank=True, null=True)
    vendors_section = models.JSONField(blank=True, null=True)
    more_info_section = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["is_icon"] = False if self.image else True
        res["image"] = get_json_if_not_none(self.image)
        res["user"] = get_summary_info(self.user)
        return res
    
    def full_json(self):
        return self.simple_json()
    


class TechnologyCoach(BaseModel):
    '''
    This model represents a technology coach.\n
    ---- FIELDS ----\n
    technology : Technology -> Technology
    email : str -> email
    community : str -> Community

    '''
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="technology_coach")
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    image = models.ForeignKey("database.Media", on_delete=models.CASCADE, null=True, blank=True)
    community = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return f"{self.technology} - {self.full_name}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["technology"] = get_summary_info(self.technology)
        res["image"] = get_json_if_not_none(self.image)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class TechnologyOverview(BaseModel):
    ''''
    This model represents a technology overview.\n
    ---- FIELDS ----\n
    technology : Technology -> Technology
    title : str -> Title of the technology
    description : str -> Description of the technology
    image : Media(optional) -> Image of the technology
    '''
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="technology_overview")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey("database.Media", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.technology}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["technology"] = get_summary_info(self.technology)
        res["image"] = get_json_if_not_none(self.image)
        return res
    
    def full_json(self) -> dict:
        return self.simple_json()
    

class TechnologyDeal(BaseModel):
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="technology_deal")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.technology}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["technology"] = get_summary_info(self.technology)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class TechnologyAction(BaseModel):
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="technology_action")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    image = models.ForeignKey("database.Media", on_delete=models.CASCADE, null=True, blank=True)
    link_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.technology} - {self.title} Action"
    

    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["technology"] = {
            "id":self.technology.id,
            "name":self.technology.name
        }
        res["image"] = get_json_if_not_none(self.image)
        return res
    
    def full_json(self):
        return self.simple_json()
    
    
class TechnologyVendor(BaseModel):
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="technology_vendor")
    vendor = models.ForeignKey("database.Vendor", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.technology} - {self.vendor}"
    
    def get_field_from_more_info(self, key):
        if self.vendor.more_info:
            return self.vendor.more_info.get(key, None)
        return None
    
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["technology"] = get_summary_info(self.technology)
        res["vendor"] = {
            **get_summary_info(self.vendor),
            "user":get_summary_info(self.vendor.user),
            "website":self.get_field_from_more_info("website"),
            "logo":get_json_if_not_none(self.vendor.logo),
            "created_via_campaign":self.get_field_from_more_info("created_via_campaign")
        }
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignTechnology(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="campaign_technology_campaign")
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="campaign_technology")

    def __str__(self):
        return f"{self.campaign} - {self.technology}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["technology"] = get_json_if_not_none(self.technology)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignCommunity(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="campaign_community")
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE)
    alias = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    help_link = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)

    def __str__(self):
        return f"{self.campaign} - {self.community}"
    
    def get_json_field_value(self, key):
        if self.info:
            return self.info.get(key, None)
        return None
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["community"] = get_summary_info(self.community)
        res["extra_links"] = self.get_json_field_value("extra_links")
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignLike(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    count = models.PositiveBigIntegerField(default=0)


    def __str__(self):
        return f"{self.campaign} - {str(self.count)} - likes"
    
    def increase_count(self):
        self.count += 1
        self.save()

    def decrease_count(self):
        self.count -= 1
        self.save()
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_json_if_not_none(self.campaign)
        return res
    
    def full_json(self):
        return self.simple_json()
    
class CampaignFollow(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, )
    user = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE, blank=True, null=True)
    zipcode = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE, blank=True, null=True)
    community_name = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.campaign} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["user"] = get_summary_info(self.user)
        res["community"] = get_summary_info(self.community)
        res["is_other"] = True if self.community.name == "Other" else False
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignTechnologyFollow(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE)
    user = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE, blank=True, null=True)
    zipcode = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE, blank=True, null=True)
    community_name = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.campaign_technology} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign_technology"] = get_summary_info(self.campaign_technology)
        res["user"] = get_summary_info(self.user)
        res["community"] = get_summary_info(self.community)
        res["is_other"] = True if self.community.name == "Other" else False
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignTechnologyLike(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE)
    user = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE, blank=True, null=True)
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE, blank=True, null=True)
    zipcode = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    community_name = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    count = models.PositiveBigIntegerField(default=0)


    def __str__(self):
        return f"{self.campaign_technology} - {self.user}"
    
    def increase_count(self):
        self.count += 1
        self.save()
    
    def decrease_count(self):
        self.count -= 1
        self.save()
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign_technology"] = get_summary_info(self.campaign_technology)
        res["user"] = get_summary_info(self.user)
        res["community"] = get_summary_info(self.community)
        return res
    
    def full_json(self):
        return self.simple_json()
    



class CampaignTechnologyView(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE)
    count = models.PositiveBigIntegerField(default=0)
    

    def __str__(self):
        return f"{self.campaign_technology} - {str(self.count)} - views"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign_technology"] = get_summary_info(self.campaign_technology)
        return res
    
    def increase_count(self):
        self.count += 1
        self.save() 
    
    def full_json(self):
        return self.simple_json()
    

class CampaignView(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    count = models.PositiveBigIntegerField(default=0)
    

    def __str__(self):
        return f"{self.campaign} - {str(self.count)} - views"
    

    def increase_count(self):
        self.count += 1
        self.save()
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        return res
    
    def full_json(self):
        return self.simple_json()
    


class CampaignManager(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="campaign_manager")
    user = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE)
    is_key_contact = models.BooleanField(blank=True, default=False)
    contact = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    role = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.campaign} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] ={
            "id":self.campaign.id,
            "title":self.campaign.title,
            "slug":self.campaign.slug
        }
        res["user"] = {
            **get_summary_info(self.user),
            "profile_picture":get_json_if_not_none(self.user.profile_picture)
        }
        return res
    
    def full_json(self):
        return self.simple_json()
    


class Comment(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE)
    user = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE) #change to email, name
    text = models.TextField(blank=True, null=True)
    status = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.status}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign_technology"] = get_summary_info(self.campaign_technology)
        res["user"] = get_summary_info(self.user)
        res["community"] = {
            **get_summary_info(self.community),
            "alias": get_comm_alias(self.campaign_technology.campaign, self.community.id)
        } if self.community else None
        return res
    
    def full_json(self):
        return self.simple_json()


class CampaignTechnologyEvent(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE, related_name="campaign_technology_event", blank=True, null=True)
    event = models.ForeignKey("database.Event", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.campaign_technology} - {self.event}"
    
    def simple_json(self)-> dict:

        res = {
            "id": self.id,
            "campaign_technology": {
            "id": self.campaign_technology.id,
            "campaign": {
                "id": self.campaign_technology.campaign.id,
                "title": self.campaign_technology.campaign.title,
                "slug": self.campaign_technology.campaign.slug,
            },
            "technology": {
                "id": self.campaign_technology.technology.id,
                "name": self.campaign_technology.technology.name,
            },
            },
            "event": {
                "id": self.event.id,
                "name": self.event.name,
                "start_date": self.event.start_date_and_time,
                "end_date": self.event.end_date_and_time,
                "description": self.event.description,
                "image": get_json_if_not_none(self.event.image),
                "event_type": self.event.event_type if self.event.event_type else "Online" if not self.event.location else "In person",
        }
        }
        return res
    
    def full_json(self):
        return self.simple_json()

    


class Partner(BaseModel):
    name = models.CharField(max_length=SHORT_STR_LEN)
    website = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    logo = models.ForeignKey("database.Media", on_delete=models.CASCADE, blank=True, null=True, related_name="partner_logo")
    phone_number = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    email = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return self.name
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["logo"] = get_json_if_not_none(self.logo)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignPartner(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="campaign_partner")
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.campaign} - {self.partner}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["partner"] = get_json_if_not_none(self.partner)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignLink(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    visits = models.PositiveBigIntegerField(default=0)
    url = models.CharField(max_length=LONG_STR_LEN, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    utm_source = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    utm_medium = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    utm_campaign = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.email} - {self.visits}"
    
    def increase_count(self):
        self.visits += 1
        self.save()

    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        return res
    
    def full_json(self):
        return self.simple_json()
    
class CampaignTechnologyTestimonial(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE, related_name="campaign_technology_testimonials")
    testimonial= models.ForeignKey("database.Testimonial",null=True, blank=True, on_delete=models.CASCADE, related_name="campaign_technology_testimonial")
    is_featured = models.BooleanField(default=False, blank=True)
    is_imported = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.campaign_technology}- {self.testimonial}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = {
            "id":self.campaign_technology.campaign.id,
            "title":self.campaign_technology.campaign.title,
            "slug":self.campaign_technology.campaign.slug
        }
        res["campaign_technology"] = {
            "id":self.campaign_technology.id,
            "technology":{
                "id":self.campaign_technology.technology.id,
                "name":self.campaign_technology.technology.name
            }
        }
        res["user"] = get_summary_info(self.testimonial.user) if self.testimonial else None
        res["community"] = {
            **get_summary_info(self.testimonial.community),
            "alias": get_comm_alias(self.campaign_technology.campaign, self.testimonial.community.id)
        } if self.testimonial.community else None
        res["image"] = get_json_if_not_none(self.testimonial.image) if self.testimonial else None
        res["body"] = self.testimonial.body if self.testimonial else None
        res["title"] = self.testimonial.title if self.testimonial else None
        res["is_approved"] = self.testimonial.is_approved if self.testimonial else None
        res["is_published"] = self.testimonial.is_published if self.testimonial else None
        return res
    
    def full_json(self):
        return self.simple_json()
    


class CampaignActivityTracking(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, blank=True, null=True)
    source = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    button_type = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    target = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


    def __str__(self):
        return f"{self.campaign} - {self.email}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_json_if_not_none(self.campaign)
        return res
    
    def full_json(self):
        return self.simple_json()
