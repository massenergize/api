from django.db import models
from django.forms import model_to_dict

from _main_.utils.base_model import BaseModel
from database.models import Event, Media, UserProfile, Community
from database.utils.common import get_summary_info
from database.utils.constants import SHORT_STR_LEN

# Create your models here.

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
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)

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
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
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
    account = models.ForeignKey(CampaignAccount, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateTimeField(null=True, blank=True)
    logo = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"{self.account} - {self.title}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["account"] = get_summary_info(self.account)
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
    
    """
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    theme = models.JSONField(blank=True, null=True)
    navigation = models.JSONField(blank=True, null=True)


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
    image = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["image"] = self.image.simple_json()
        return res
    
    def full_json(self):
        return self.simple_json()
    


class TechnologyCoach(BaseModel):
    '''
    This model represents a technology coach.\n
    ---- FIELDS ----\n
    technology : Technology -> Technology
    user : UserProfile -> User
    community : str -> Community

    '''
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE) # create a an account for coaches that are not on the platform
    community = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return f"{self.technology} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["technology"] = get_summary_info(self.technology)
        res["user"] = get_summary_info(self.user)
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
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.technology}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["technology"] = get_summary_info(self.technology)
        res["image"] = self.image.simple_json()
        return res
    
    def full_json(self) -> dict:
        return self.simple_json()
    


class Vendor(BaseModel):
    """
    This model represents a vendor.\n
    ---- FIELDS ----\n
    name : str -> Name of the vendor
    description : str -> Description of the vendor
    logo : Media(optional) -> Logo of the vendor
    email : str(optional) -> Email of the vendor
    website : str(optional) -> Website of the vendor
    phone_number : str(optional) -> Phone number of the vendor
    zipcode : str(optional) -> Zipcode of the vendor
    is_verified : bool -> Whether the vendor is verified
    creator : UserProfile -> UserProfile of the vendor
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    website = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    phone_number = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    zipcode = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    is_verified = models.BooleanField(default=False)
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="vendor_creator")
    service_area = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return self.name
    

    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["logo"] = self.logo.simple_json()
        return res
    
    def full_json(self):
        return self.simple_json()
    
class TechnologyVendor(BaseModel):
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

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
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.campaign} - {self.technology}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["technology"] = get_summary_info(self.technology)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignCommunity(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

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
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE) #user with email and zipcode
    zipcode = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.campaign} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["user"] = get_summary_info(self.user)
        return res
    
    def full_json(self):
        return self.simple_json()
    
class CampaignFollow(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE) #user with email and zipcode
    zipcode = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.campaign} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["user"] = get_summary_info(self.user)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignTechnologyLike(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE) #user with email and zipcode
    zipcode = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.campaign_technology} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign_technology"] = get_summary_info(self.campaign_technology)
        res["user"] = get_summary_info(self.user)
        return res
    
    def full_json(self):
        return self.simple_json()
    



class CampaignTechnologyView(BaseModel):
    campaign_technology = models.ForeignKey(CampaignTechnology, on_delete=models.CASCADE)
    ip_address = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    user_agent = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.campaign_technology} - {self.ip_address}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign_technology"] = get_summary_info(self.campaign_technology)
        return res
    
    def full_json(self):
        return self.simple_json()
    


class CampaignManager(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_key_contact = models.BooleanField(blank=True, default=False)
    contact = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.campaign} - {self.user}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["user"] = get_summary_info(self.user)
        return res
    
    def full_json(self):
        return self.simple_json()
    


class Comment(BaseModel):
    campaign_technology = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    status = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return f"{self.user} - {self.status}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign_technology"] = get_summary_info(self.campaign_technology)
        res["user"] = get_summary_info(self.user)
        return res
    
    def full_json(self):
        return self.simple_json()


class CampaignEvent(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_featured = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return f"{self.campaign} - {self.event}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["event"] = get_summary_info(self.event)
        return res
    
    def full_json(self):
        return self.simple_json()
    


class Partner(BaseModel):
    name = models.CharField(max_length=SHORT_STR_LEN)
    website = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    logo = models.ForeignKey(Media, on_delete=models.CASCADE, blank=True, null=True, related_name="partner_logo")
    phone_number = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
    email = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)

    def __str__(self):
        return self.name
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignPartner(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.campaign} - {self.partner}"
    
    def simple_json(self)-> dict:
        res = super().to_json()
        res.update(model_to_dict(self))
        res["campaign"] = get_summary_info(self.campaign)
        res["partner"] = get_summary_info(self.partner)
        return res
    
    def full_json(self):
        return self.simple_json()
    

class CampaignLink(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    visits = models.PositiveBigIntegerField(default=0)
    email = models.EmailField(blank=True, null=True)

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