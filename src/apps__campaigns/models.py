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
    subdomain = models.CharField(max_length=SHORT_STR_LEN, unique=True)
    creator = models.ForeignKey("database.UserProfile", on_delete=models.CASCADE, null=True, blank=True)
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"name:  {self.name}"

    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        return res

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
    role = models.CharField(blank=True, max_length=255)


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
    communities_section = models.JSONField(blank=True, null=True) # {title, description} of communities section


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
    navigation = models.JSONField(blank=True, null=True)
    advert = models.JSONField(blank=True, null=True)


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
    icon = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return self.name
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["is_icon"] = False if self.image else True
        res["image"] = get_json_if_not_none(self.image)
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
    
class TechnologyVendor(BaseModel):
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="technology_vendor")
    vendor = models.ForeignKey("database.Vendor", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.technology} - {self.vendor}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["technology"] = get_summary_info(self.technology)
        res["vendor"] = get_summary_info(self.vendor)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignTechnology(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="campaign_technology_campaign")
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name="campaign_technology")

    overview_title  = models.CharField(max_length=255, blank=True, null=True)
    action_section  = models.JSONField(blank=True, null=True)
    coaches_section = models.JSONField(blank=True, null=True)
    deal_section_image = models.ForeignKey("database.Media", on_delete=models.CASCADE, null=True, blank=True)
    deal_section = models.JSONField(blank=True, null=True)
    vendors_section = models.JSONField(blank=True, null=True)
    more_info_section = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.campaign} - {self.technology}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["technology"] = get_summary_info(self.technology)
        res["deal_section_image"] = get_json_if_not_none(self.deal_section_image)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignCommunity(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="campaign_community")
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE)
    help_link = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)

    def __str__(self):
        return f"{self.campaign} - {self.community}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["community"] = get_summary_info(self.community)
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

    def __str__(self):
        return f"{self.campaign} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
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
        res["community"] = get_summary_info(self.community)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignTechnologyEvent(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE, related_name="campaign_technology_event", blank=True, null=True)
    event = models.ForeignKey("database.Event", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.campaign_technology} - {self.event}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign_technology)
        res["event"] = {
            "id":self.event.id,
            "name":self.event.name,
            "start_date":self.event.start_date_and_time,
            "end_date":self.event.end_date_and_time,
            "description":self.event.description,
            "image":get_json_if_not_none(self.event.image),
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
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, blank=True, null=True)
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE, related_name="campaign_technology_testimonials")
    title = models.CharField(max_length=SHORT_STR_LEN, db_index=True, blank=True, null=True)
    body = models.TextField(max_length=LONG_STR_LEN, blank=True, null=True)
    is_approved = models.BooleanField(default=False, blank=True)
    image = models.ForeignKey("database.Media", on_delete=models.SET_NULL,null=True, blank=True,related_name="campaign_technology_testimonial_image")
    created_by = models.ForeignKey( "database.UserProfile", on_delete=models.CASCADE, db_index=True, null=True)
    is_published = models.BooleanField(default=False, blank=True)
    anonymous = models.BooleanField(default=False, blank=True)
    community = models.ForeignKey("database.Community", on_delete=models.CASCADE, blank=True, null=True, db_index=True)

    def __str__(self):
        return f"{self.campaign} - {self.campaign_technology}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["campaign_technology"] = get_summary_info(self.campaign_technology)
        res["user"] = get_summary_info(self.created_by)
        res["community"] = get_summary_info(self.community)
        res["image"] = get_json_if_not_none(self.image)
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
