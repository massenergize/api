from django.db import models
from django.contrib.postgres.fields import JSONField
from database.utils.constants import *
from datetime import date, datetime
from django.utils import timezone
from .utils.common import  json_loader,get_json_if_not_none, get_summary_info
from django.forms.models import model_to_dict
from carbon_calculator.models import Action as CCAction
import uuid

CHOICES = json_loader('./database/raw_data/other/databaseFieldChoices.json')
ZIP_CODE_AND_STATES = json_loader('./database/raw_data/other/states.json')

class Location(models.Model):
  """
  A class used to represent a geographical region.  It could be a complete and
  proper address or just a city name, zipcode, county etc

  Attributes
  ----------
  type : str
    the type of the location, whether it is a full address, zipcode only, etc
  street : str
    The street number if it is available
  city : str
    the name of the city if available
  county : str
    the name of the county if available
  state: str
    the name of the state if available
  more_info: JSON
    any anotheraction() dynamic information we would like to store about this location 
  """
  id = models.AutoField(primary_key=True)
  location_type = models.CharField(max_length=TINY_STR_LEN, 
    choices=CHOICES["LOCATION_TYPES"].items())
  street = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  unit_number = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  zipcode = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  city = models.CharField(max_length=SHORT_STR_LEN, blank=True) 
  county = models.CharField(max_length=SHORT_STR_LEN, blank=True) 
  is_deleted = models.BooleanField(default=False, blank=True)
  state = models.CharField(max_length=SHORT_STR_LEN, 
    choices = ZIP_CODE_AND_STATES.items(), blank=True)
  more_info = JSONField(blank=True, null=True)

  def __str__(self):
    if self.location_type == 'STATE_ONLY':
      return self.state
    elif self.location_type == 'ZIP_CODE_ONLY':
      return self.zipcode
    elif self.location_type == 'CITY_ONLY':
      return self.city
    elif self.location_type == 'COUNTY_ONLY':
      return self.county 
    elif self.location_type == 'FULL_ADDRESS':
      return '%s, %s, %s, %s, %s' % (
        self.street, self.unit_number, self.city, self.county, self.state
      )
    
    return self.location_type

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    return self.simple_json()

  class Meta:
    db_table = 'locations'


class Media(models.Model):
  """
  A class used to represent any Media that is uploaded to this website

  Attributes
  ----------
  name : SlugField
    The short name for this media.  It cannot only contain letters, numbers,
    hypens and underscores.  No spaces allowed.
  file : File
    the file that is to be stored.
  media_type: str
    the type of this media file whether it is an image, video, pdf etc.
  """
  id = models.AutoField(primary_key=True)
  name = models.SlugField(max_length=SHORT_STR_LEN, blank=True) 
  file = models.FileField(upload_to='media/')
  media_type = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  order = models.PositiveIntegerField(default=0, blank=True, null=True)


  def __str__(self):      
    return self.name


  def simple_json(self):
    return {
      "id": self.id,
      "url": self.file.url,
    }

  def full_json(self):
    return {
      "id": self.id,
      "name": self.name,
      "url": self.file.url,
      "media_type": self.media_type
    }
  class Meta:
    db_table = "media"
    ordering = ('order', 'name')

class Policy(models.Model):
  """
   A class used to represent a Legal Policy.  For instance the 
   Terms and Agreement Statement that users have to agree to during sign up.


  Attributes
  ----------
  name : str
    name of the Legal Policy
  description: str
    the details of this policy
  communities_applied:
    how many communities this policy applies to.
  is_global: boolean
    True if this policy should apply to all the communities
  info: JSON
    dynamic information goes in here
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=LONG_STR_LEN, db_index = True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  is_global = models.BooleanField(default=False, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  more_info = JSONField(blank=True, null=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):
    return self.name

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    res  =  model_to_dict(self)
    community = self.community_set.all().first()
    if community:
      res['community'] = get_json_if_not_none(community)
    return res


  class Meta:
    ordering = ('name',)
    db_table = 'legal_policies'
    verbose_name_plural = "Legal Policies"


class Goal(models.Model):
  """
  A class used to represent a Goal 

  Attributes
  ----------
  name : str
    A short title for this goal
  status: str
    the status of this goal whether it has been achieved or not.
  description:
    More details about this goal 
  created_at: DateTime
    The date and time that this goal was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this goal
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN)
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)

  target_number_of_households = models.PositiveIntegerField(default=0, blank=True)
  target_number_of_actions = models.PositiveIntegerField(default=0, blank=True)
  target_carbon_footprint_reduction = models.PositiveIntegerField(default=0, blank=True)

  attained_number_of_households = models.PositiveIntegerField(default=0, blank=True)
  attained_number_of_actions = models.PositiveIntegerField(default=0, blank=True)
  attained_carbon_footprint_reduction = models.PositiveIntegerField(default=0, blank=True)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  more_info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)


  def get_status(self):
    return CHOICES["GOAL_STATUS"][self.status]

  def __str__(self):
    return f"{self.name} {' - Deleted' if self.is_deleted else ''}"

  def simple_json(self):
    return model_to_dict(self, exclude=['is_deleted'])

  def full_json(self):
    return self.simple_json()

  class Meta:
    db_table = 'goals'


class Community(models.Model):
  """
  A class used to represent a Community on this platform.

  Attributes
  ----------
  name : str
    The short name for this Community
  subdomain : str (can only contain alphabets, numbers, hyphen and underscores)
    a primary unique identifier for this Community.  They would need the same 
    to access their website.  For instance if the subdomain is wayland they 
    would access their portal through wayland.massenergize.org
  owner: JSON
    information about the name, email and phone of the person who is supposed 
    to be owner and main administrator when this Community account is opened.
  logo : int
    Foreign Key to Media that holds logo of community
  banner : int
    Foreign Key to Media that holds logo of community
  is_geographically_focused: boolean
    Information about whether this community is geographically focused or 
    dispersed
  is_approved: boolean
    This field is set to True if the all due diligence has been done by the 
    Super Admins and the community is not allowed to operate.
  created_at: DateTime
    The date and time that this community was created 
  policies: ManyToMany
    policies created by community admins for this community
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this community
  more_info: JSON
    any another dynamic information we would like to store about this location 
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN)
  subdomain = models.SlugField(max_length=SHORT_STR_LEN, unique=True)
  owner_name = models.CharField(max_length=SHORT_STR_LEN, default='Ellen')
  owner_email = models.EmailField(blank=False)
  owner_phone_number = models.CharField(blank=True, null=True, max_length=SHORT_STR_LEN)
  about_community = models.TextField(max_length=LONG_STR_LEN, blank=True)
  logo = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    null=True, blank=True, related_name='community_logo')
  banner = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    null=True, blank=True, related_name='community_banner')
  goal = models.ForeignKey(Goal, blank=True, null=True, on_delete=models.SET_NULL)
  is_geographically_focused = models.BooleanField(default=False, blank=True)
  location = JSONField(blank=True, null=True)
  policies = models.ManyToManyField(Policy, blank=True)
  is_approved = models.BooleanField(default=False, blank=True)
  accepted_terms_and_conditions = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  more_info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):      
    return self.name

  def info(self):
    return model_to_dict(self, ['id', 'name', 'subdomain'])

  def simple_json(self):
    res = model_to_dict(self, ['id', 'name', 'subdomain', 'is_approved', 'owner_phone_number',
      'owner_name', 'owner_email', 'is_geographically_focused', 'is_published', 'is_approved'])
    res['logo'] = get_json_if_not_none(self.logo)
    return res

  def full_json(self):
    admin_group: CommunityAdminGroup = CommunityAdminGroup.objects.filter(community__id=self.pk).first()
    if admin_group:
      admins = [a.simple_json() for a in admin_group.members.all()]
    else:
      admins = []

    # get the community goal
    goal = get_json_if_not_none(self.goal) or {}
    # decision not to include state reported solar in this total
    #solar_actions_count = Data.objects.get(name__icontains="Solar", community=self).reported_value
    # 
    # For Wayland launch, insisting that we show large numbers so people feel good about it.
    goal["attained_number_of_households"] += (RealEstateUnit.objects.filter(community=self).count())
    goal["attained_number_of_actions"] += (UserActionRel.objects.filter(real_estate_unit__community=self, status="DONE").count())

    return {
      "id": self.id,
      "name": self.name,
      "subdomain": self.subdomain,
      "owner_name": self.owner_name,
      "owner_email": self.owner_email,
      "owner_phone_number": self.owner_phone_number,
      "goal": goal,
      "about_community": self.about_community,
      "logo":get_json_if_not_none(self.logo),
      "location":self.location,
      "is_approved": self.is_approved,
      "is_published": self.is_published,
      "is_geographically_focused": self.is_geographically_focused,
      "banner":get_json_if_not_none(self.banner),
      "created_at": self.created_at,
      "updated_at": self.updated_at,
      "more_info": self.more_info,
      "admins": admins
    }


  class Meta:
    verbose_name_plural = "Communities"
    db_table = "communities"


class RealEstateUnit(models.Model):
  """
  A class used to represent a Real Estate Unit. 

  Attributes
  ----------
  unit_type : str
    The type of this unit eg. Residential, Commercial, etc
  location: Location
    the geographic address or location of this real estate unit
  created_at: DateTime
    The date and time that this real estate unity was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this real estate unit
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN)
  unit_type =  models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["REAL_ESTATE_TYPES"].items()
  )
  community = models.ForeignKey(Community, null=True, on_delete=models.SET_NULL, blank=True)
  location = JSONField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False, blank=True)

  def is_commercial(self):
    return self.unit_type == 'C'

  def is_residential(self):
    return self.unit_type == 'R'

  def __str__(self):
    return f"{self.community}|{self.unit_type}|{self.name}"

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    return self.simple_json()


  class Meta:
    db_table = 'real_estate_units'


class Role(models.Model):
  """
  A class used to represent  Role for users on the MassEnergize Platform

  Attributes
  ----------
  name : str
    name of the role
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=TINY_STR_LEN, 
    choices=CHOICES["ROLE_TYPES"].items(), 
    unique=True
  ) 
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)


  def __str__(self):
    return CHOICES["ROLE_TYPES"][self.name] 

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    return self.simple_json()


  class Meta:
    ordering = ('name',)
    db_table = 'roles'



class UserProfile(models.Model):
  """
  A class used to represent a MassEnergize User

  Note: Authentication is handled by firebase so we just need emails

  Attributes
  ----------
  email : str
    email of the user.  Should be unique.
  user_info: JSON
    a JSON representing the name, bio, etc for this user.
  bio:
    A short biography of this user
  is_super_admin: boolean
    True if this user is an admin False otherwise
  is_community_admin: boolean
    True if this user is an admin for a community False otherwise
  is_vendor: boolean
    True if this user is a vendor False otherwise
  other_info: JSON
    any another dynamic information we would like to store about this UserProfile 
  created_at: DateTime
    The date and time that this goal was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this goal

  #TODO: roles field: if we have this do we need is_superadmin etc? also why
  #  not just one?  why many to many
  """
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
  full_name=models.CharField(max_length=SHORT_STR_LEN, null=True)
  profile_picture = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    blank=True, null=True)
  preferred_name=models.CharField(max_length=SHORT_STR_LEN, null=True)
  email = models.EmailField(unique=True, db_index=True)
  user_info = JSONField(blank=True, null=True)
  real_estate_units = models.ManyToManyField(RealEstateUnit, 
    related_name='user_real_estate_units', blank=True)
  goal = models.ForeignKey(Goal, blank=True, null=True, on_delete=models.SET_NULL)
  communities = models.ManyToManyField(Community, blank=True)
  roles = models.ManyToManyField(Role, blank=True) 
  is_super_admin = models.BooleanField(default=False, blank=True)
  is_community_admin = models.BooleanField(default=False, blank=True)
  is_vendor = models.BooleanField(default=False, blank=True)
  other_info = JSONField(blank=True, null=True)
  accepts_terms_and_conditions = models.BooleanField(default=False, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False, blank=True)

  def __str__(self):
    return self.email

  def info(self):
    return model_to_dict(self, ['id', 'email', 'full_name'])

  def simple_json(self):
    res =  model_to_dict(self, ['id', 'full_name', 'preferred_name', 'email', 'is_super_admin', 'is_community_admin'])
    res['user_info'] = self.user_info
    res['profile_picture'] = get_json_if_not_none(self.profile_picture)
    res['communities'] = [c.community.name for c in CommunityMember.objects.filter(user=self)]
    return res


  def full_json(self):
    team_members = [t.team.info() for t in TeamMember.objects.filter(user=self)]
    community_members = CommunityMember.objects.filter(user=self)
    communities = [cm.community.info() for cm in community_members]
    admin_at = [cm.community.info() for cm in CommunityMember.objects.filter(user=self, is_admin=True)]
    
    data = model_to_dict(self, exclude=['real_estate_units', 
      'communities', 'roles'])
    admin_at = [get_json_if_not_none(c.community) for c in self.communityadmingroup_set.all()]
    data['households'] = [h.simple_json() for h in self.real_estate_units.all()]
    data['goal'] = get_json_if_not_none(self.goal)
    data['communities'] = communities
    data['admin_at'] = admin_at
    data['teams'] = team_members
    data['profile_picture'] = get_json_if_not_none(self.profile_picture)
    return data

  class Meta:
    db_table = 'user_profiles' 


class CommunityMember(models.Model):
  id = models.AutoField(primary_key=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE)
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  is_admin = models.BooleanField(blank=True, default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False, blank=True)


  def __str__(self):
    return f"{self.user} is {'an ADMIN' if self.is_admin else 'a MEMBER'} in Community({self.community})"

  def simple_json(self):
    res =  model_to_dict(self, ['id', 'is_admin'])
    res['community'] = get_summary_info(self.community)
    res['user'] = get_summary_info(self.user)
    return res

  def full_json(self):
    return self.simple_json()

  class Meta:
    db_table = 'community_members_and_admins'
    unique_together = [['community', 'user']]


class Subdomain(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
  community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, related_name="subdomain_community")
  in_use = models.BooleanField(default=False, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"{self.community} - {self.name}"

  def simple_json(self):
    res =  model_to_dict(self, ['id', 'in_use', 'name', 'created_at', 'updated_at'])
    res['community'] = get_summary_info(self.community)
    return res

  def full_json(self):
    return self.simple_json()

  class Meta:
    db_table = 'subdomains'

class Team(models.Model):
  """
  A class used to represent a Team in a community

  Attributes
  ----------
  name : str
    name of the team
  description: str
    description of this team 
  admins: ManyToMany
    administrators for this team
  members: ManyToMany
    the team members
  community:
    which community this team is a part of
  logo:
    Foreign Key to Media file represtenting the logo for this team    
  banner:
    Foreign Key to Media file represtenting the banner for this team
  created_at: DateTime
    The date and time that this goal was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this goal
  """
  id = models.AutoField(primary_key=True)
  #Team names should be unique globally
  name = models.CharField(max_length=SHORT_STR_LEN)
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  admins = models.ManyToManyField(UserProfile, related_name='team_admins', 
    blank=True) 
  members = models.ManyToManyField(UserProfile, related_name='team_members', 
    blank=True) 
  community = models.ForeignKey(Community, on_delete=models.CASCADE)
  goal = models.ForeignKey(Goal, blank=True, null=True, on_delete=models.SET_NULL)
  logo = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    null=True, blank=True, related_name='team_logo')
  banner = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    null=True, blank=True, related_name='team_banner')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def is_admin(self, UserProfile):
    return self.admins.filter(id=UserProfile.id)

  def is_member(self, UserProfile):
    return self.members.filter(id=UserProfile.id)

  def __str__(self):
    return self.name

  def info(self):
    return model_to_dict(self, ['id', 'name', 'description'])

  def simple_json(self):
    res =  self.info()
    res['community'] = get_json_if_not_none(self.community)
    res['logo'] = get_json_if_not_none(self.logo)
    return res

  def full_json(self):
    data = self.simple_json()
    data['admins'] = [a.simple_json() for a in self.admins.all()]
    data['members'] = [m.simple_json() for m in self.members.all()]
    data['goal'] = get_json_if_not_none(self.goal)
    data['banner'] = get_json_if_not_none(self.banner)
    return data


  class Meta:
    ordering = ('name',)
    db_table = 'teams'
    unique_together = [['community', 'name']]

class TeamMember(models.Model):
  id = models.AutoField(primary_key=True)
  team = models.ForeignKey(Team, on_delete=models.CASCADE)
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  is_admin = models.BooleanField(blank=True, default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False, blank=True)


  def __str__(self):
    return f"{self.user} is {'an ADMIN' if self.is_admin else 'a MEMBER'} in Team({self.team})"

  def simple_json(self):
    res =  model_to_dict(self, ['id', 'is_admin'])
    res['team'] = get_summary_info(self.team)
    res['user'] = get_summary_info(self.user)
    return res

  def full_json(self):
    return self.simple_json()

  class Meta:
    db_table = 'team_members_and_admins'
    unique_together = [['team', 'user']]

class Service(models.Model):
  """
  A class used to represent a Service provided by a Vendor

  Attributes
  ----------
  name : str
    name of the service
  description: str
    description of this service
  image: int
    Foreign Key to a Media file represtenting an image for this service if any    
  icon: str
    a string description of an icon class for this service if any
  info: JSON
    any another dynamic information we would like to store about this Service 
  created_at: DateTime
    The date and time that this goal was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this goal
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN,unique=True)
  description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  service_location = JSONField(blank=True, null=True)
  image = models.ForeignKey(Media, blank=True, null=True, 
    on_delete=models.SET_NULL)
  icon = models.CharField(max_length=SHORT_STR_LEN,blank=True)
  info = JSONField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return self.name

  def simple_json(self):
    return model_to_dict(self, ['id', 'name', 'description', 'service_location', 'icon'])

  def full_json(self):
    return self.simple_json()


  class Meta:
    db_table = 'services'




class ActionProperty(models.Model):
  """
  A class used to represent an Action property.

  Attributes
  ----------
  name : str
    name of the Vendor
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
  short_description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)


  def __str__(self): 
    return self.name

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    return self.full_json()

  class Meta:
    verbose_name_plural = "Properties"
    ordering = ('id',)
    db_table = 'action_properties'


class TagCollection(models.Model):
  """
  A class used to represent a collection of Tags.

  Attributes
  ----------
  name : str
    name of the Tag Collection
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length = SHORT_STR_LEN, unique=True)
  is_global = models.BooleanField(default=False, blank=True)
  allow_multiple = models.BooleanField(default=False)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)
  rank = models.PositiveIntegerField(default=0)


  def __str__(self):
    return self.name


  def simple_json(self):
    res =  model_to_dict(self)
    res['tags'] = [t.simple_json() for t in self.tag_set.all()]
    return res


  def full_json(self):
    return self.simple_json()


  class Meta:
    ordering = ('name',)
    db_table = 'tag_collections'


class Tag(models.Model):
  """
  A class used to represent an Tag.  It is essentially a string that can be 
  used to describe or group items, actions, etc
  
  Attributes
  ----------
  name : str
    name of the Tag
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length = SHORT_STR_LEN)
  points = models.PositiveIntegerField(null=True, blank=True)
  icon = models.CharField(max_length = SHORT_STR_LEN, blank = True)
  tag_collection = models.ForeignKey(TagCollection, null=True, 
    on_delete=models.CASCADE, blank=True)
  rank = models.PositiveIntegerField(default=0)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):
    return "%s - %s" % (self.name, self.tag_collection)

  def simple_json(self):
    res = model_to_dict(self)
    res['order'] = self.rank
    res['tag_collection_name'] = None if not self.tag_collection else self.tag_collection.name
    return res


  def full_json(self):
    data = self.simple_json()
    data['tag_collection'] = get_json_if_not_none(self.tag_collection)
    return data

  class Meta:
    ordering = ('rank',)
    db_table = 'tags'
    unique_together = [['rank', 'name', 'tag_collection']]



class Vendor(models.Model):
  """
  A class used to represent a Vendor/Contractor that provides a service 
  associated with any of the actions.

  Attributes
  ----------
  name : str
    name of the Vendor
  description: str
    description of this service
  logo: int
    Foreign Key to Media file represtenting the logo for this Vendor    
  banner: int
    Foreign Key to Media file represtenting the banner for this Vendor  
  address: int
    Foreign Key for Location of this Vendor
  key_contact: int
    Foreign Key for MassEnergize User that is the key contact for this vendor
  service_area: str
    Information about whether this vendor provides services nationally, 
    statewide, county or Town services only
  properties_services: str
    Whether this vendor services Residential or Commercial units only
  onboarding_date: DateTime
    When this vendor was onboard-ed on the MassEnergize Platform for this 
      community
  onboarding_contact:
    Which MassEnergize Staff/User onboard-ed this vendor
  verification_checklist:
    contains information about some steps and checks needed for due diligence 
    to be done on this vendor eg. Vendor MOU, Reesearch
  is_verified: boolean
    When the checklist items are all done and verified then set this as True
    to confirm this vendor
  more_info: JSON
    any another dynamic information we would like to store about this Service 
  created_at: DateTime
    The date and time that this Vendor was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this Vendor
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN,unique=True)
  phone_number = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  email = models.EmailField(blank=True, null=True, db_index=True)
  description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  logo = models.ForeignKey(Media, blank=True, null=True, 
    on_delete=models.SET_NULL, related_name='vender_logo')
  banner = models.ForeignKey(Media, blank=True, null=True, 
    on_delete=models.SET_NULL, related_name='vendor_banner')
  address = JSONField(blank=True, null=True)
  key_contact = JSONField(blank=True, null=True)
  service_area = models.CharField(max_length=SHORT_STR_LEN)
  service_area_states = JSONField(blank=True, null=True)
  services = models.ManyToManyField(Service, blank=True)
  properties_serviced = JSONField(blank=True, null=True) 
  onboarding_date = models.DateTimeField(auto_now_add=True)
  onboarding_contact = models.ForeignKey(UserProfile, blank=True, 
    null=True, on_delete=models.SET_NULL, related_name='onboarding_contact')
  verification_checklist = JSONField(blank=True, null=True) 
  is_verified = models.BooleanField(default=False, blank=True)
  location = JSONField(blank=True, null=True)
  more_info = JSONField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  communities = models.ManyToManyField(Community, blank=True)
  tags = models.ManyToManyField(Tag, related_name='vendor_tags', blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return self.name

  def info(self):
    return model_to_dict(self, ['id', 'name', 'service_area', 'key_contact', 'phone_number', 'email' ])

  def simple_json(self):
    data = model_to_dict(self, exclude=[
     'logo', 'banner', 'services', 'onboarding_contact', 'more_info', 'services','communities'
    ])
    data['services'] = [s.simple_json() for s in self.services.all()]
    data['communities'] = [c.simple_json() for c in self.communities.all()]
    data['tags'] = [t.simple_json() for t in self.tags.all()]
    data['logo'] = get_json_if_not_none(self.logo)
    return data


  def full_json(self):
    data =  model_to_dict(self, exclude=['logo', 'banner', 'services', 'onboarding_contact', 'more_info'])
    data['onboarding_contact'] = get_json_if_not_none(self.onboarding_contact)
    data['logo'] = get_json_if_not_none(self.logo)
    data['tags'] = [t.simple_json() for t in self.tags.all()]
    data['banner']  = get_json_if_not_none(self.banner)
    data['services'] = [s.simple_json() for s in self.services.all()]
    data['communities'] = [c.simple_json() for c in self.communities.all()]
    return data

  class Meta:
    db_table = 'vendors'


class Action(models.Model):
  """
  A class used to represent an Action that can be taken by a user on this 
  website. 

  Attributes
  ----------
  title : str
    A short title for this Action.
  is_global: boolean
    True if this action is a core action that every community should see or not.
    False otherwise.
  about: str
    More descriptive information about this action.
  steps_to_take: str
    Describes the steps that can be taken by an a user for this action;
  icon: str
    a string description of the icon class for this action if any
  image: int Media
    a Foreign key to an uploaded media file
  average_carbon_score:
    the average carbon score for this action as given by the carbon calculator
  geographic_area: str
    the Location where this action can be taken
  created_at: DateTime
    The date and time that this real estate unity was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this real estate unit
  """
  id = models.AutoField(primary_key=True)
  title = models.CharField(max_length = SHORT_STR_LEN, db_index=True)
  is_global = models.BooleanField(default=False, blank=True)
  featured_summary = models.TextField(max_length = LONG_STR_LEN, blank=True, null=True)
  steps_to_take = models.TextField(max_length = LONG_STR_LEN, blank=True)
  deep_dive = models.TextField(max_length = LONG_STR_LEN, blank=True)
  about = models.TextField(max_length = LONG_STR_LEN, 
    blank=True)
  tags = models.ManyToManyField(Tag, related_name='action_tags', blank=True)
  geographic_area = JSONField(blank=True, null=True)
  icon = models.CharField(max_length = SHORT_STR_LEN, blank=True)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    null=True,blank=True)
  properties = models.ManyToManyField(ActionProperty, blank=True)
  vendors = models.ManyToManyField(Vendor, blank=True)
  calculator_action = models.ForeignKey(CCAction, blank=True, null=True, on_delete=models.SET_NULL)
  average_carbon_score = models.TextField(max_length = SHORT_STR_LEN, 
    blank=True)
  community = models.ForeignKey(Community, on_delete=models.SET_NULL, 
    null=True, blank=True, db_index=True)
  rank = models.PositiveSmallIntegerField(default = 0, blank=True) 
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self): 
    return self.title

  def info(self):
    return model_to_dict(self, ['id','title'])

  def simple_json(self):
    data =  model_to_dict(self, ['id','is_published', 'is_deleted', 'title', 'is_global', 'icon', 'rank', 
      'average_carbon_score', 'featured_summary'])
    data['image'] = get_json_if_not_none(self.image)
    data['calculator_action'] = get_summary_info(self.calculator_action)
    data['tags'] = [t.simple_json() for t in self.tags.all()]
    data['steps_to_take'] = self.steps_to_take
    data['deep_dive'] = self.deep_dive
    data['about'] = self.about
    data['community'] = get_summary_info(self.community)
    data['vendors'] = [v.info() for v in self.vendors.all()]
    return data

  def full_json(self):
    data  = self.simple_json()
    data['is_global'] = self.is_global
    data['steps_to_take'] = self.steps_to_take
    data['about'] = self.about
    data['geographic_area'] = self.geographic_area
    data['properties'] = [p.simple_json() for p in self.properties.all()]
    data['vendors'] = [v.simple_json() for v in self.vendors.all()]
    return data


  class Meta:
    ordering = ['rank', 'title']
    db_table = 'actions'
    unique_together = [['title', 'community']]


class Event(models.Model):
  """
  A class used to represent an Event.

  Attributes
  ----------
  name : str
    name of the event
  description: str
    more details about this event
  start_date_and_time: Datetime
    when the event starts (both the day and time)
  end_date_and_time: Datetime
    when the event ends
  location: Location
    where the event is taking place
  tags: ManyToMany
    tags on this event to help in easily filtering
  image: Media
    Foreign key linking to the image attached to this event.
  archive: boolean
    True if this event should be archived
  is_global: boolean
    True if this action is an event that every community should see or not.
    False otherwise.
  """
  id = models.AutoField(primary_key=True)
  name  = models.CharField(max_length = SHORT_STR_LEN)
  featured_summary = models.TextField(max_length = LONG_STR_LEN, blank=True, null=True)
  description = models.TextField(max_length = LONG_STR_LEN)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True)
  invited_communities = models.ManyToManyField(Community, 
    related_name="invited_communites", blank=True)
  start_date_and_time  = models.DateTimeField(db_index=True)
  end_date_and_time  = models.DateTimeField(db_index=True)
  location = JSONField(blank=True, null=True)
  tags = models.ManyToManyField(Tag, blank=True)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True,blank=True)
  archive =  models.BooleanField(default=False, blank=True)
  is_global = models.BooleanField(default=False, blank=True)
  external_link = models.CharField(max_length = SHORT_STR_LEN, blank=True)
  is_external_event = models.BooleanField(default=False, blank=True)
  more_info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)
  rank = models.PositiveIntegerField(default=0, blank=True, null=True)


  def __str__(self):             
    return self.name

  def simple_json(self):
    data = model_to_dict(self, exclude=['tags', 'image', 'community'])
    data['start_date_and_time'] = self.start_date_and_time
    data['end_date_and_time'] = self.end_date_and_time
    data['tags'] = [t.simple_json() for t in self.tags.all()]
    data['community'] = get_json_if_not_none(self.community)
    data['image'] = None if not self.image else self.image.full_json()
    data['more_info'] = self.more_info
    return data


  def full_json(self):
    return self.simple_json()


  class Meta:
    ordering = ('rank', '-start_date_and_time',)
    db_table = 'events'


class EventAttendee(models.Model):
  """
  A class used to represent events and attendees

  Attributes
  ----------
  attendee : str
    name of the Vendor
  status: str
    Tells if the attendee is just interested, RSVP-ed or saved for later.
  event: int
    Foreign Key to event that the attendee is going to.
  """
  id = models.AutoField(primary_key=True)
  attendee =  models.ForeignKey(UserProfile,on_delete=models.CASCADE, 
    db_index=True)
  event =  models.ForeignKey(Event,on_delete=models.CASCADE)
  status = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["EVENT_CHOICES"].items()
  )
  is_deleted = models.BooleanField(default=False, blank=True)

  def __str__(self):
    return '%s | %s | %s' % (
      self.attendee, CHOICES["EVENT_CHOICES"][self.status], self.event)
  
  def simple_json(self):
    data =  model_to_dict(self, ['id', 'status'])
    data['attendee'] = get_json_if_not_none(self.attendee)
    data['event'] = get_json_if_not_none(self.event)
    return data

  def full_json(self):
    return self.simple_json()


  class Meta:
    verbose_name_plural = "Event Attendees"
    db_table = 'event_attendees'
    unique_together=[['attendee', 'event']]



class Permission(models.Model):

  """
   A class used to represent Permission(s) that are required by users to perform 
   any tasks on this platform.


  Attributes
  ----------
  name : str
    name of the Vendor
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["PERMISSION_TYPES"].items(), 
    db_index=True
  )
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)


  def __str__(self):
    return CHOICES["PERMISSION_TYPES"][self.name] 

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    return self.simple_json()

  class Meta:
    ordering = ('name',)
    db_table = 'permissions'

    
class UserPermissions(models.Model):
  """
  A class used to represent Users and what they can do.

  Attributes
  ----------
  who : int
    the user on this site
  can_do: int
    Foreign Key desscribing the policy that they can perform
  """
  id = models.AutoField(primary_key=True)
  who = models.ForeignKey(Role,on_delete=models.CASCADE)
  can_do = models.ForeignKey(Permission, on_delete=models.CASCADE)
  is_deleted = models.BooleanField(default=False, blank=True)

  def __str__(self):
    return '(%s) can (%s)' % (self.who, self.can_do)

  def simple_json(self):
    return {
      "id": self.id,
      "who": get_json_if_not_none(self.who),
      "can_do": get_json_if_not_none(self.can_do)
    }

  def full_json(self):
    return self.simple_json()

  class Meta:
    ordering = ('who',)
    db_table = 'user_permissions'


class Testimonial(models.Model):
  """
   A class used to represent a Testimonial shared by a user.


  Attributes
  ----------
  title : str
    title of the testimony
  body: str (HTML)
    more information for this testimony.  
  is_approved: boolean
    after the community admin reviews this, he can check the box
  """
  id = models.AutoField(primary_key=True)
  title = models.CharField(max_length=SHORT_STR_LEN, db_index=True)
  body = models.TextField(max_length=LONG_STR_LEN)
  is_approved = models.BooleanField(default=False, blank=True)
  tags = models.ManyToManyField(Tag, blank=True)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    null=True, blank=True)
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_index=True, null=True)
  action = models.ForeignKey(Action, on_delete=models.CASCADE, null=True, db_index=True)
  vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, 
    null=True, blank=True, db_index=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, 
    blank=True, null=True, db_index=True)
  rank = models.PositiveSmallIntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True, blank=True)
  updated_at = models.DateTimeField(auto_now=True, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)
  anonymous = models.BooleanField(default=False, blank=True)
  preferred_name = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
  other_vendor = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)

  def __str__(self):        
    return self.title

  def info(self):
    return model_to_dict(self, include=['id', 'title', 'community'])

  def simple_json(self):
    anonymous = {
      "full_name": "Anonymous",
      "email": "anonymous"
    }
    res = model_to_dict(self, exclude=['image', 'tags'])
    res["user"] = get_json_if_not_none(self.user) or  anonymous
    res["action"] = get_json_if_not_none(self.action)
    res["vendor"] = None if not self.vendor else self.vendor.info()
    res["community"] = get_json_if_not_none(self.community)
    res["created_at"] = self.created_at
    res['file'] = get_json_if_not_none(self.image)
    res['tags'] = [t.simple_json() for t in self.tags.all()]
    res['anonymous'] = self.anonymous
    res['preferred_name'] = self.preferred_name
    res['other_vendor'] = self.other_vendor
    return res

  def full_json(self):
    data = self.simple_json() 
    data['image'] = data.get('file', None)
    data['tags'] = [t.simple_json() for t in self.tags.all()]
    return data

  class Meta:
    ordering = ('rank',)
    # unique_together = [['user', 'action']]
    db_table = 'testimonials'


class UserActionRel(models.Model):
  """
   A class used to represent a user and his/her relationship with an action.
   Whether they marked an action as todo, done, etc


  Attributes
  ----------
  user : int
    Foreign Key for user
  real_estate_unit:
    Foreign key for the real estate unit this action is related to.
  action: int
    which action they marked 
  vendor:
    which vendor they choose to contact/connect with 
  testimonial:
    what they had to say about this action.
  status: 
    Whether they marked it as todo, done or save for later  
  """
  id = models.AutoField(primary_key=True)
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_index=True)
  real_estate_unit = models.ForeignKey(RealEstateUnit, on_delete=models.CASCADE)
  action = models.ForeignKey(Action, on_delete=models.CASCADE)
  vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, 
    null=True, blank=True)
  status  = models.CharField(max_length=SHORT_STR_LEN, 
    choices = CHOICES["USER_ACTION_STATUS"].items(), 
    db_index=True, default='TODO')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_deleted = models.BooleanField(default=False, blank=True)

  def simple_json(self):
    return {
      "id": self.id,
      "user": get_json_if_not_none(self.user),
      "action": get_json_if_not_none(self.action),
      "real_estate_unit": get_json_if_not_none(self.real_estate_unit),
      "status": self.status
    }

  def full_json(self):
    res = self.simple_json()
    res["vendor"] = get_json_if_not_none(self.vendor)
    return res

  def __str__(self):
    return  "%s | %s | (%s)" % (self.user, self.status, self.action)

  class Meta:
    ordering = ('status','user', 'action')
    unique_together = [['user', 'action', 'real_estate_unit']]


class CommunityAdminGroup(models.Model):
  """
  This represents a binding of a group of users and a community for which they
  are admin for.

  Attributes
  ----------
  name : str
    name of the page section
  info: JSON
    dynamic information goes in here
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True, db_index=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, blank=True)
  members = models.ManyToManyField(UserProfile, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  pending_admins = JSONField(blank=True, null=True)

  def __str__(self):
    return self.name

  def simple_json(self):
    res = model_to_dict(self, exclude=['members'])
    res['community'] = get_json_if_not_none(self.community)
    res['members'] = [m.simple_json() for m in self.members.all()]
    return res


  def full_json(self):
   return self.simple_json()

  class Meta:
    ordering = ('name',)
    db_table = 'community_admin_group'


class UserGroup(models.Model):
  """
  This represents a binding of a group of users and a community 
  and the permissions they have.

  Attributes
  ----------
  name : str
    name of the page section
  info: JSON
    dynamic information goes in here
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True, db_index=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, 
    blank=True, db_index=True)
  members = models.ManyToManyField(UserProfile, blank=True)
  permissions = models.ManyToManyField(Permission, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)

  def __str__(self):
    return self.name

  def simple_json(self):
    return model_to_dict(self, exclude=['members', 'permissions'])

  def full_json(self):
    data = self.simple_json()
    data['community'] = get_json_if_not_none(self.community)
    data['members'] = [m.simple_json() for m in self.members.all()]
    data['permissions'] = [p.simple_json() for p in self.permissions.all()]
    return data


  class Meta:
    ordering = ('name',)
    db_table = 'user_groups'


class Data(models.Model):
  """Instances of data points

  Attributes
  ----------
  name : str
    name of the statistic
  value: decimal
    The value of the statistic goes here
  info: JSON
    dynamic information goes in here.  The symbol and other info goes here
  community: int
    foreign key linking a community to this statistic
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length = SHORT_STR_LEN, db_index=True)
  value =  models.PositiveIntegerField(default=0)
  reported_value =  models.PositiveIntegerField(default=0)
  denominator =  models.CharField(max_length = SHORT_STR_LEN, blank=True)
  symbol = models.CharField(max_length = LONG_STR_LEN, blank=True)
  tag = models.ForeignKey(Tag, blank=True, on_delete=models.CASCADE, 
    null=True, db_index=True )
  community = models.ForeignKey(Community, blank=True,  
    on_delete=models.SET_NULL, null=True, db_index=True)
  info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)

  def __str__(self):         
    return "%s | %s (%d) |(%s)" % (self.community, self.name, self.value,  self.tag)

  def simple_json(self):
    return model_to_dict(self, fields=["id", "name", "value", "reported_value"])

  def full_json(self):
    data = self.simple_json()
    data["tag"] = get_json_if_not_none(self.tag)
    data["community"] =  get_json_if_not_none(self.community)
    return data

  class Meta:
    verbose_name_plural = "Data"
    ordering = ('name','value')
    db_table = 'data'


class Graph(models.Model):
  """Instances keep track of a statistic from the admin

  Attributes
  ----------
  title : str
    the title of this graph
  type: str
    the type of graph to be plotted eg. pie chart, bar chart etc
  data: JSON
    data to be plotted on this graph
  """
  id = models.AutoField(primary_key=True)
  title = models.CharField(max_length = LONG_STR_LEN, db_index=True)
  graph_type = models.CharField(max_length=TINY_STR_LEN, 
    choices=CHOICES["GRAPH_TYPES"].items())
  community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True,blank=True)
  data = models.ManyToManyField(Data,  blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)


  def simple_json(self):
    return model_to_dict(self, fields=["title", "community", "is_published"])


  def full_json(self):
    res =  self.simple_json()
    res["data"] = [d.simple_json() for d in self.data.all()]
    return res


  def __str__(self):   
    return self.title

  class Meta:
    verbose_name_plural = "Graphs"
    ordering = ('title',)


class Button(models.Model):
  """Buttons on the pages"""
  text = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  icon = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  url = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  color = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)

  def __str__(self):        
    return self.text

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    return self.simple_json()

  class Meta:
    ordering = ('text',)


class SliderImage(models.Model):
  """Model the represents the database for Images that will be 
  inserted into slide shows
  
  Attributes
  ----------
  title : str
    title of the page section
  subtitle: str
    sub title for this image as should appear on the slider
  buttons: JSON
    a json list of buttons with each containing text, link, icon, color etc
  """
  id = models.AutoField(primary_key=True)
  title = models.CharField(max_length = LONG_STR_LEN, blank=True, db_index=True)
  subtitle = models.CharField(max_length = LONG_STR_LEN, blank=True)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True,blank=True)
  buttons = models.ManyToManyField(Button, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return self.title

  def simple_json(self):
    return {
      "id": self.id,
      "title": self.title,
      "image": get_json_if_not_none(self.image),
    }

  def full_json(self):
    res =  self.simple_json()
    res['buttons'] = [b.simple_json() for b in self.buttons.all()]
    return res

  class Meta:
    verbose_name_plural = "Slider Images"
    db_table = "slider_images"


class Slider(models.Model):
  """
  Model that represents a model for a slider/carousel on the website

  Attributes
  ----------
  name : str
    name of the page section
  description: str
    a description of this slider
  info: JSON
    dynamic information goes in here
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length = LONG_STR_LEN, blank=True, db_index=True)
  description = models.CharField(max_length = LONG_STR_LEN, blank=True)
  slides = models.ManyToManyField(SliderImage, blank=True)
  is_global = models.BooleanField(default=False, blank=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return self.name

  def simple_json(self):
    return {
      "id": self.id,
      "name": self.name,
      "description": self.description,
    }

  def full_json(self):
    res =  self.simple_json()
    res['slides'] = [s.full_json() for s in self.slides.all()]
    return res


class Menu(models.Model):
  """Represents items on the menu/navigation bar (top-most bar on the webpage)
  Attributes
  ----------
  name : str
    name of the page section
  content: JSON
    the content is represented as a json
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=LONG_STR_LEN, unique=True)
  content = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):              
    return self.name

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    return self.simple_json()

  class Meta:
    ordering = ('name',)


class Card(models.Model):
  """Buttons on the pages"""
  title = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  icon = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  link = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  media = models.ForeignKey(Media, blank=True, 
    on_delete=models.SET_NULL, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)

  def __str__(self):
    return self.title

  def simple_json(self):
    return {
      "title": self.title,
      "description": self.description,
      "icon": self.icon,
      "link": self.link,
      "media": get_json_if_not_none(self.media)
    }

  def full_json(self):
    return self.simple_json()

  class Meta:
    ordering = ('title',)

class PageSection(models.Model):
  """
   A class used to represent a PageSection
   #TODO: what about page sections like a gallery, slideshow, etc?

  Attributes
  ----------
  name : str
    name of the page section
  info: JSON
    dynamic information goes in here
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN)
  title = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    null=True, blank=True)
  cards = models.ManyToManyField(Card, blank=True)
  buttons = models.ManyToManyField(Button, blank=True)
  slider = models.ForeignKey(Slider, on_delete=models.SET_NULL, 
    null=True, blank=True)
  graphs = models.ManyToManyField(Graph, blank=True, related_name='graphs')
  info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return self.name

  def simple_json(self):
    return model_to_dict(self, ['id', 'name', 'title', 'description'])

  def full_json(self):
    res = self.simple_json()
    res['image'] = get_json_if_not_none(self.image)
    res["cards"]= [c.simple_json() for c in self.cards.all()]
    res["buttons"]= [b.simple_json() for b in self.buttons.all()],
    res["slider"] = get_json_if_not_none(self.slider, True),
    res["graphs"] = [g.full_json() for g in self.graphs.all()],
    res["info"] = self.info
    return res

class Page(models.Model):
  """
   A class used to represent a Page on a community portal
   eg. The home page, about-us page, etc

  Attributes
  ----------
  title : str
    title of the page
  description: str
    the description of the page
  community: int
    Foreign key for which community this page is linked to
  sections: ManyToMany
    all the different parts/sections that go on this page
  content: JSON
    dynamic info for this page goes here.
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=LONG_STR_LEN, db_index=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
  sections = models.ManyToManyField(PageSection, blank=True)
  info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return f"{self.name} - {self.community.name}"

  def simple_json(self):
    res = model_to_dict(self, ['id', 'name', 'description'])
    res["community"] = get_json_if_not_none(self.community)
    return res

  def full_json(self):
    res = self.simple_json()
    res["sections"] =  [s.full_json() for s in self.sections.all()]
    res["info"] =  self.info
    return res

  class Meta:
    unique_together = [['name', 'community']]



class BillingStatement(models.Model):
  """
   A class used to represent a Billing Statement

  Attributes
  ----------
  name : str
    name of the statement.
  amount: decimal
    the amount of money owed
  description:
    the breakdown of the bill for this community
  community: int
    Foreign Key to the community to whom this bill is associated.
  start_date: Datetime
    the start date from which the charges were incurred
  end_date:
    the end date up to which this charge was incurred.
  more_info: JSON
    dynamic information goes in here
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=SHORT_STR_LEN)
  amount = models.CharField(max_length=SHORT_STR_LEN, default='0.0')
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  start_date = models.DateTimeField(blank=True, db_index=True)
  end_date = models.DateTimeField(blank=True)
  more_info = JSONField(blank=True, null=True)
  community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, db_index=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):
    return self.name

  def simple_json(self):
    res = model_to_dict(self, exclude=['community'])
    res['community'] = get_json_if_not_none(self.community)
    return res


  def full_json(self):
    return self.simple_json()

  class Meta:
    ordering = ('name',)
    db_table = 'billing_statements'

class Subscriber(models.Model):
  """
   A class used to represent a subscriber / someone who wants to join the 
   massenergize mailist

  Attributes
  ----------
  name : str
    name of the statement.
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length = SHORT_STR_LEN)
  email = models.EmailField(blank=False, db_index=True)
  community = models.ForeignKey(Community,on_delete=models.SET_NULL, 
    null=True, db_index=True)
  is_deleted = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return self.name

  def simple_json(self):
    res = model_to_dict(self)
    res['community'] = None if not self.community else self.community.info()
    return res

  def full_json(self):
    return self.simple_json()


  class Meta:
    db_table = 'subscribers'
    unique_together = [['email', 'community']]


class EmailCategory(models.Model):
  """
  A class tha represents an email preference that a user or subscriber can
  subscribe to.

  Attributes
  ----------
  name : str
    the name for this email preference
  community: int
    Foreign Key to the community this email category is associated with
  is_global: boolean
    True if this email category should appear in all the communities
  """
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length = SHORT_STR_LEN, db_index=True)
  community = models.ForeignKey(Community, db_index=True, 
    on_delete=models.CASCADE)
  is_global = models.BooleanField(default=False, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return self.name

  def simple_json(self):
    return model_to_dict(self)

  def full_json(self):
    res = self.simple_json()
    res['community'] = get_json_if_not_none(self.community)
    return res

  class Meta:
    db_table = 'email_categories'
    unique_together = [['name', 'community']]
    verbose_name_plural = "Email Categories"


class SubscriberEmailPreference(models.Model):
  """
  Represents the email preferences of each subscriber.
  For a subscriber might want marketing emails but not promotion emails etc

  Attributes
  ----------
  subscriber: int
    Foreign Key to a subscriber 
  email_category: int
    Foreign key to an email category
  """
  id = models.AutoField(primary_key=True)
  subscriber = models.ForeignKey(Subscriber,
    on_delete=models.CASCADE, db_index=True)
  subscribed_to = models.ForeignKey(EmailCategory,on_delete=models.CASCADE)
  is_deleted = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return "%s - %s" % (self.subscriber, self.subscribed_to)

  def simple_json(self):
    return {
      "id": self.id,
      "subscriber": get_json_if_not_none(self.subscriber),
      "subscribed_to": get_json_if_not_none(self.subscribed_to)
    }

  def full_json(self):
    return self.simple_json()

  class Meta:
    db_table = 'subscriber_email_preferences'

class HomePageSettings(models.Model):
  id = models.AutoField(primary_key=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
  title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  images = models.ManyToManyField(Media, blank=True)

  featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  featured_links = JSONField(blank=True, null=True)
  featured_events = models.ManyToManyField(Event, blank=True)
  featured_stats = models.ManyToManyField(Data, blank=True)

  show_featured_events =  models.BooleanField(default=True, blank=True)
  show_featured_stats = models.BooleanField(default=True, blank=True)
  show_featured_links = models.BooleanField(default=True, blank=True)
  show_featured_video = models.BooleanField(default=False, blank=True)

  is_template = models.BooleanField(default=False, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)

  def __str__(self):             
    return "HomePageSettings - %s" % (self.community)

  def simple_json(self):
    res =  model_to_dict(self, exclude=[
      'images', 'featured_events', 'featured_stats'
    ])
    return res


  def full_json(self):
    goal = get_json_if_not_none(self.community.goal) or {}
    # decision not to include state reported solar
    #solar_actions_count = Data.objects.get(name__icontains="Solar", community=self.community).reported_value
    # 
    # For Wayland launch, insisting that we show large numbers so people feel good about it.
    goal["organic_attained_number_of_households"] = (RealEstateUnit.objects.filter(community=self.community).count())
    goal["organic_attained_number_of_actions"] = (UserActionRel.objects.filter(real_estate_unit__community=self.community,status="DONE").count())

    res =  self.simple_json()
    res['images'] = [i.simple_json() for i in self.images.all()]
    res['community'] = get_json_if_not_none(self.community)
    res['featured_events'] = [i.simple_json() for i in self.featured_events.all()]
    res['featured_stats'] = [i.simple_json() for i in self.featured_stats.all()]
    res['goal']  = goal
    return res

  class Meta:
    db_table = 'home_page_settings'
    verbose_name_plural = "HomePageSettings"


class ActionsPageSettings(models.Model):
  id = models.AutoField(primary_key=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
  title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  images = models.ManyToManyField(Media, blank=True)
  more_info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)
  is_template = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return "ActionsPageSettings - %s" % (self.community)

  def simple_json(self):
    res =  model_to_dict(self, exclude=['images'])
    res['community'] = get_json_if_not_none(self.community)
    return res


  def full_json(self):
    res =  self.simple_json()
    res['images'] = [i.simple_json() for i in self.images]
    res['community'] = get_json_if_not_none(self.community)
    return res

  class Meta:
    db_table = 'actions_page_settings'
    verbose_name_plural = "ActionsPageSettings"

class ContactUsPageSettings(models.Model):
  id = models.AutoField(primary_key=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
  title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  images = models.ManyToManyField(Media, blank=True)
  more_info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)
  is_template = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return "ContactUsPageSettings - %s" % (self.community)

  def simple_json(self):
    res =  model_to_dict(self, exclude=['images'])
    res['community'] = get_json_if_not_none(self.community)
    return res


  def full_json(self):
    res =  self.simple_json()
    res['images'] = [i.simple_json() for i in self.images.all()]
    return res

  class Meta:
    db_table = 'contact_us_page_settings'
    verbose_name_plural = "ContactUsPageSettings"


class DonatePageSettings(models.Model):
  id = models.AutoField(primary_key=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE,  db_index=True)
  title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  donation_link = models.CharField(max_length=LONG_STR_LEN, blank=True)
  sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  images = models.ManyToManyField(Media, blank=True)
  more_info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)
  is_template = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return "DonatePageSettings - %s" % (self.community)

  def simple_json(self):
    res =  model_to_dict(self, exclude=['images'])
    res['community'] = get_json_if_not_none(self.community)
    return res


  def full_json(self):
    res =  self.simple_json()
    res['images'] = [i.simple_json() for i in self.images.all()]
    return res

  class Meta:
    db_table = 'donate_page_settings'
    verbose_name_plural = "DonatePageSettings"


class AboutUsPageSettings(models.Model):
  id = models.AutoField(primary_key=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE,  db_index=True)
  title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank = True)
  images = models.ManyToManyField(Media, blank=True)
  more_info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)
  is_template = models.BooleanField(default=False, blank=True)


  def __str__(self):             
    return "AboutUsPageSettings - %s" % (self.community)

  def simple_json(self):
    res =  model_to_dict(self, exclude=['images'])
    res['community'] = get_json_if_not_none(self.community)
    return res


  def full_json(self):
    res =  self.simple_json()
    res['images'] = [i.simple_json() for i in self.images.all()]
    return res

  class Meta:
    db_table = 'about_us_page_settings'
    verbose_name_plural = "AboutUsPageSettings"


class ImpactPageSettings(models.Model):
  id = models.AutoField(primary_key=True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE, 
   db_index=True)
  title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  featured_video_link = models.TextField(max_length=SHORT_STR_LEN, blank = True)
  images = models.ManyToManyField(Media, blank=True)
  more_info = JSONField(blank=True, null=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  is_published = models.BooleanField(default=True)
  is_template = models.BooleanField(default=False, blank=True)

  def __str__(self):             
    return "ImpactPageSettings - %s" % (self.community)

  def simple_json(self):
    res =  model_to_dict(self, exclude=['images'])
    res['community'] = get_json_if_not_none(self.community)
    return res


  def full_json(self):
    res =  self.simple_json()
    res['images'] = [i.simple_json() for i in self.images.all()]
    return res

  class Meta:
    db_table = 'impact_page_settings'
    verbose_name_plural = "ImpactPageSettings"


class Message(models.Model):
  """
  A class used to represent  Role for users on the MassEnergize Platform

  Attributes
  ----------
  name : str
    name of the role
  """
  id = models.AutoField(primary_key=True)
  user_name = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True) 
  title = models.CharField(max_length=SHORT_STR_LEN) 
  uploaded_file = models.ForeignKey(Media, blank=True, null=True, on_delete=models.SET_NULL) 
  email = models.EmailField(blank=True) 
  user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True) 
  body = models.TextField(max_length=LONG_STR_LEN)
  community = models.ForeignKey(Community, blank=True, on_delete=models.SET_NULL, null=True)
  team = models.ForeignKey(Team, blank=True, on_delete=models.SET_NULL, null=True)
  have_replied = models.BooleanField(default=False, blank=True)
  have_forwarded = models.BooleanField(default=False, blank=True)
  is_team_admin_message = models.BooleanField(default=False, blank=True)
  is_deleted = models.BooleanField(default=False, blank=True)
  archive = models.BooleanField(default=False, blank=True)
  starred = models.BooleanField(default=False, blank=True)
  response = models.CharField(max_length=LONG_STR_LEN, blank=True, null=True) 
  created_at = models.DateTimeField(auto_now_add=True, null=True)


  def __str__(self):
    return f"{self.title}"

  def simple_json(self):
    res = model_to_dict(self)
    res["community"] = get_summary_info(self.community)
    res["team"] = get_summary_info(self.team)
    return res

  def full_json(self):
    res = self.simple_json()
    res["uploaded_file"] = get_json_if_not_none(self.uploaded_file)
    return res


  class Meta:
    ordering = ('title',)
    db_table = 'messages'


class ActivityLog(models.Model):
  """
  A class used to represent  Activity Log on the MassEnergize Platform

  Attributes
  ----------
  """
  id = models.AutoField(primary_key=True)
  path = models.CharField(max_length=SHORT_STR_LEN, default='/') 
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True) 
  community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True) 
  created_at = models.DateTimeField(auto_now_add=True)
  status = models.CharField(max_length=SHORT_STR_LEN, default='success', blank=True) 
  trace = JSONField(blank=True, null=True) 
  request_body = JSONField(blank=True, null=True) 
  # add response or error field

  def __str__(self):
    return self.path

  def simple_json(self):
    return  model_to_dict(self)

  def full_json(self):
    res = self.simple_json()
    res["user"] = get_json_if_not_none(self.user)
    res["community"] = get_json_if_not_none(self.community)
    return res


  class Meta:
    ordering = ('path',)
    db_table = 'activity_logs'


class Deployment(models.Model):
  """
  A class used to represent  Activity Log on the MassEnergize Platform

  Attributes
  ----------
  """
  id = models.AutoField(primary_key=True)
  version = models.CharField(max_length=SHORT_STR_LEN, default='') 
  deploy_commander = models.CharField(max_length=SHORT_STR_LEN, default='', blank=True) 
  notes = models.CharField(max_length=LONG_STR_LEN, default='', blank=True) 
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.version

  def simple_json(self):
    return  model_to_dict(self)

  def full_json(self):
    return self.simple_json()


  class Meta:
    db_table = 'deployments'
    ordering = ('-version',)

