from django.db import models
from django.contrib.postgres.fields import JSONField
from .utils.constants import *
from datetime import date, datetime
import django.contrib.auth.models as auth_models
from .utils import common

#TODO: check typos
#TODO: enforce optional fields with blank=True
#TODO: ensure adding json field to collect more info
#TODO: Documentation
#TODO: add verbose name plural to some fields
#TODO: add indexes to some models
#TODO: change some text field to html field?

CHOICES = common.json_loader('./database/raw_data/other/database.json')
ZIP_CODE_AND_STATES = common.json_loader('./database/raw_data/other/states.json')
API_URL = 'https://api.massenergize.org'


class Location(models.Model):
  """
  A class used to represent the notion of a geographical Location: be it a 
  proper full address or city name or even just a zipcode.

  Attributes
  ----------
  name : str
    The name of this Location
  type : str
    the type of the location, whether it is a full address, zipcode only, etc
  street : str
    The street number if it is available
  city : str
    the name of the city if available
  state: str
  more_info: JSON
    any another dynamic information we would like to store about this location 

  Methods
  -------
  describe()
    Returns a good summary/description of the location.
  """
  name = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  location_type = models.CharField(max_length=TINY_STR_LEN, 
    choices=CHOICES["LOCATION_TYPES"].items())
  street = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  unit_number = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  zipcode = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  city = models.CharField(max_length=SHORT_STR_LEN, blank=True) 
  state = models.CharField(max_length=SHORT_STR_LEN, 
    choices = ZIP_CODE_AND_STATES.items(), blank=True)
  more_info = JSONField()

  def __str__(self):
    #TODO: rewrite to account for all possible missing data
    return "%s, %s" % (self.type, self.name)


  def describe(self):
    return str(self)

class Media(models.Model):
  """
  A class used to represent any Media that is uploaded to this website

  Attributes
  ----------
  name : SludField
    The short name for this media.  It cannot only contain letters, numbers,
    hypens and underscores.  No spaces allowed.
  file : File
    the file that is to be stored.
  media_type: str
    the type of this media file whether it is an image, video, pdf etc.
  """
  name = models.SlugField(max_length=SHORT_STR_LEN) #can't have spaces
  file = models.FileField(upload_to='files/')
  media_type = models.CharField(max_length=SHORT_STR_LEN, 
    choices=CHOICES["FILE_TYPES_ALLOWED"].items(), default='UNKNOWN')
  def get_url(self):
    return '%s/files/%s' (API_URL, self.name)


  def __str__(self):      
    return self.name

  class Meta:
    db_table = "files"
    ordering = ('name',)


class Community(models.Model):
  """
  A class used to represent the notion of a Community. 

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
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this community
  more_info: JSON
    any another dynamic information we would like to store about this location 
  """
  name = models.CharField(max_length=SHORT_STR_LEN)
  subdomain = models.SlugField(max_length=SHORT_STR_LEN, unique=True)
  owner = JSONField() 
  about_you = models.TextField(max_length=LONG_STR_LEN)
  logo = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True, related_name='community_logo')
  banner = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True, related_name='community_banner')
  is_geographically_focused = models.BooleanField(default=False)
  location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
  is_approved = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  more_info = JSONField()


  def __str__(self):      
    return self.name

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
  unit_type =  models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["REAL_ESTATE_TYPES"].items()
  )
  location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def is_commercial(self):
    return self.unit_type == 'C'

  def is_residential(self):
    return self.unit_type == 'R'

  def __str__(self):
    return '%s: %s, %s, %s, %s' % (
      self.unit_type, self.street, self.city, self.zipcode, self.state
    )

  class Meta:
    db_table = 'real_estate_units'


class Goal(models.Model):
  """
  A class used to represent a Goal 

  Attributes
  ----------
  title : str
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
  title = models.CharField(max_length=SHORT_STR_LEN)
  status = models.CharField(
    max_length=TINY_STR_LEN, choices=CHOICES["GOAL_STATUS"].items())
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def get_status(self):
    return CHOICES["GOAL_STATUS"][self.status]

  def __str__(self):
    return self.title

  class Meta:
    db_table = 'goals'


class UserProfile(models.Model):
  """
  A class used to represent a MassEnergize User

  Attributes
  ----------
  user_account : int [User]
    Foreign Key that represents a user
  address: int [Location]
    Foregin Key that represents the Location for this user
  bio:
    A short biography of this user
  is_super_admin: boolean
    True if this user is an admin False otherwise
  is_community_admin: boolean
    True if this user is an admin for a community False otherwise
  is_vendor: boolean
    True if this user is a vendor False otherwise
  other_info: JSON
    any another dynamic information we would like to store about this location 
  created_at: DateTime
    The date and time that this goal was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this goal
  """

  user_account = models.ForeignKey(auth_models.User, 
    on_delete=models.CASCADE, null=True)
  bio = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  address = models.ForeignKey(RealEstateUnit, blank=True, 
    on_delete=models.SET_NULL, 
    null=True) #TODO: delete
  real_estate_units = models.ManyToManyField(RealEstateUnit, 
    related_name='user_real_estate_units')
  goals = models.ManyToManyField(Goal)
  communities = models.ManyToManyField(Community)
  is_super_admin = models.BooleanField(default=False)
  is_community_admin = models.BooleanField(default=False)
  is_vendor = models.BooleanField(default=False)
  age_acknowledgment = models.BooleanField() #TODO: delete
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  other_info = JSONField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

def __str__(self):
  return self.user_account.get_full_name()


class Meta:
  db_table = 'people' #TODO: change to user_profiles


class Team(models.Model):
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
  description = models.TextField(max_length=LONG_STR_LEN)
  admins = models.ManyToManyField(UserProfile, related_name='team_admins') 
  members = models.ManyToManyField(UserProfile, related_name='team_members') 
  goals = models.ManyToManyField(Goal) 
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def is_admin(self, UserProfile):
    return self.members.filter(id=UserProfile.id)

  def is_member(self, UserProfile):
    return self.members.filter(id=UserProfile.id)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'teams'


class Service(models.Model):
  name = models.CharField(max_length=SHORT_STR_LEN,unique=True)
  description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  service_location = models.ForeignKey(Location, on_delete=models.SET_NULL, 
    null=True, blank=True)
  info = JSONField()


  def __str__(self):             
    return self.name

  class Meta:
    db_table = 'services'



class Vendor(models.Model):
  name = models.CharField(max_length=SHORT_STR_LEN,unique=True)
  address = models.ForeignKey(Location, blank=True, null=True, 
    on_delete=models.SET_NULL)
  key_contact = models.ForeignKey(UserProfile, blank=True, null=True, 
    on_delete=models.SET_NULL, related_name='key_contact')
  service_area = models.CharField(max_length=TINY_STR_LEN, 
    choices=CHOICES["SERVICE_AREAS"].items())
  services = models.ManyToManyField(Service)
  properties_serviced = models.CharField(max_length=TINY_STR_LEN, 
    choices=CHOICES["PROPERTIES_SERVICED"].items())
  onboarding_date = models.DateTimeField(default=datetime.now)
  onboarding_contact = models.ForeignKey(UserProfile, blank=True, 
    null=True, on_delete=models.SET_NULL, related_name='onboarding_contact')
  description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  verification_checklist = JSONField() #include Vendor MOU, Reesearch
  is_verified = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  more_info = JSONField()

  def __str__(self):             
    return self.name

  class Meta:
    db_table = 'vendors'


class ActionProperty(models.Model):
  title = models.CharField(max_length=SHORT_STR_LEN, blank = True, unique=True)
  short_description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  community = models.ManyToManyField(Community)
  order_position = models.PositiveSmallIntegerField(default=0)

  def __str__(self): 
    return "%s: %s" % (self.order_position, self.name)

  class Meta:
    verbose_name_plural = "Properties"
    ordering = ('order_position',)
    db_table = 'action_properties'


class ActionCategory(models.Model):
  title = models.CharField(max_length = SHORT_STR_LEN, unique=True)
  icon = models.CharField(max_length = SHORT_STR_LEN, blank = True)
  community = models.ManyToManyField(Community)
  order_position = models.PositiveSmallIntegerField(default = 0)

  def __str__(self):        
    return "%d: %s" % (self.order_position, self.name)

  
  class Meta:
    verbose_name_plural = "Action Categories"
    ordering = ('order_position',)
    db_table = ('action_categories')


class Tag(models.Model):
  value = models.CharField(max_length = SHORT_STR_LEN, primary_key=True)

  def __str__(self):
    return self.value

  class Meta:
    ordering = ('value',)
    db_table = 'tags'


class TagCategory(models.Model):
  name = models.CharField(max_length = SHORT_STR_LEN, primary_key=True)
  tags = models.ManyToManyField(Tag)
  def __str__(self):
    return self.value

  class Meta:
    ordering = ('name',)
    db_table = 'tag_categories'


class Action(models.Model):
  """
  A class used to represent an Action that can be taken by a user on this 
  website. 

  Attributes
  ----------
  title : str
    A short title for this Action.
  is_template_action: boolean
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
  geographic_area: str
    the Location where this action can be taken
  created_at: DateTime
    The date and time that this real estate unity was added 
  created_at: DateTime
    The date and time of the last time any updates were made to the information
    about this real estate unit
  """
  title = models.CharField(max_length = SHORT_STR_LEN)
  is_template_action = models.BooleanField(default=False)
  steps_to_take = models.TextField(max_length = LONG_STR_LEN, blank=True)
  about = models.TextField(max_length = LONG_STR_LEN, 
    blank=True)
  tags = models.ManyToManyField(Tag, related_name='action_tags')
  geographic_area = models.ForeignKey(Location, 
    null=True, blank=True, 
    on_delete=models.SET_NULL)
  icon = models.CharField(max_length = SHORT_STR_LEN)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True,blank=True)
  properties = models.ManyToManyField(ActionProperty)
  vendors = models.ManyToManyField(Vendor)
  community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True)
  category = models.ManyToManyField(ActionCategory) 
  rank = models.PositiveSmallIntegerField(default = 0) 
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self): 
    return self.title


  class Meta:
    ordering = ['rank', 'title']
    db_table = 'actions'
    unique_together = [['title', 'community']]


class Event(models.Model):
  title  = models.CharField(max_length = SHORT_STR_LEN)
  description = models.TextField(max_length = LONG_STR_LEN)
  community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True)
  start_date_and_time  = models.DateTimeField(default=datetime.now)
  end_date_and_time  = models.DateTimeField(default=datetime.now)
  #TODO: make this a Location foreign key field?
  location = models.CharField(max_length = SHORT_STR_LEN, blank=True) 
  tags = models.ManyToManyField(Tag)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True,blank=True)
  archive =  models.BooleanField(default=False)

  #TODO: make sure any one who retrieves events only retrieves those that are 
  #not past

  def __str__(self):             
    return self.title

  class Meta:
    ordering = ('-start_date_and_time',)
    db_table = 'events'


class EventUserRel(models.Model):
  choice = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["EVENT_CHOICES"].items()
  )
  user =  models.ForeignKey(UserProfile,on_delete=models.CASCADE)
  event =  models.ForeignKey(Event,on_delete=models.CASCADE)

  def __str__(self):
    return '%s - %s' % (self.user, self.event)


class Permission(models.Model):
  """
  Represents the Permissions that are required by users to perform any tasks 
  on this platform.
  """
  permission_type = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["PERMISSION_TYPES"].items(), 
    primary_key=True
  ) 

  def can_approve(self):
    return self.permission_type == 'A';


  def can_create(self):
    return self.permission_type == 'C';

  
  def can_edit(self):
    return self.permission_type == 'E';


  def can_fork(self):
    return self.permission_type == 'F';


  def can_view(self):
    return self.permission_type == 'V';


  def __str__(self):
    return 'Can: %s' %  CHOICES["PERMISSION_TYPES"][self.permission_type] 

  class Meta:
    ordering = ('permission_type',)
    db_table = 'permissions'

    

class Role(models.Model):
  role_type = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["ROLE_TYPES"].items(), 
    primary_key=True
  ) 


  def is_super_admin(self):
    return self.role_type == 'S'


  def is_community_admin(self):
    return self.role_type == 'C'

  
  def is_team_admin(self):
    return self.role_type == 'T'

  
  def is_unit_admin(self):
    return self.role_type == 'R'


  def is_default_user(self):
    return self.role_type == 'U'

  def is_vendor_admin(self):
    return self.role_type == 'V'

  def __str__(self):
    return 'Is: %s' % CHOICES["ROLE_TYPES"][self.role_type] 

  class Meta:
    ordering = ('role_type',)
    db_table = 'roles'


class UserPolicy(models.Model):
  who = models.ForeignKey(Role,on_delete=models.CASCADE)
  can_do = models.ForeignKey(Permission, on_delete=models.CASCADE)
  #TODO: add with_what field?

  def __str__(self):
    return '(%s) can (%s)' % (self.who, self.can_do)

  class Meta:
    ordering = ('who',)
    db_table = 'user_policies'


class Notification(models.Model):
  title = models.CharField(max_length=SHORT_STR_LEN)
  body = models.CharField(max_length=LONG_STR_LEN, blank=True)

  def __str__(self):
    return self.title

  class Meta:
    ordering = ('title',)
    db_table = 'notifications'


class Testimonial(models.Model):
  rank = models.PositiveSmallIntegerField(default=0)
  name = models.CharField(max_length=SHORT_STR_LEN)
  text = models.TextField(max_length=LONG_STR_LEN)
  is_approved = models.BooleanField(default=False)
  date = models.DateTimeField(default=datetime.now)
  file = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True)

  def __str__(self):        
    return "%d: %s" % (self.rank, self.name)

  class Meta:
    ordering = ('rank',)
    db_table = 'testimonials'

  
class ActionTaken(models.Model):
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  real_estate_unit = models.ForeignKey(RealEstateUnit, on_delete=models.CASCADE)
  action = models.ForeignKey(Action, on_delete=models.CASCADE)
  vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, 
    null=True, blank=True)
  testimonial = models.ForeignKey(Testimonial, on_delete=models.SET_NULL, 
    null=True, blank=True)
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  info = JSONField()

  def __str__(self):
    return  "%s: %s" % (self.user, self.action)


class CommunityAdminGroup(models.Model):
  """
  This represents a binding of a group of users and a community for which they
  are admin for.
  """
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
  description = models.TextField(max_length=LONG_STR_LEN)
  community = models.ForeignKey(Community, on_delete=models.CASCADE)
  members = models.ManyToManyField(UserProfile)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'community_admin_group'


class UserGroup(models.Model):
  """
  This represents a binding of a group of users and a community for which they
  are admin for.
  """
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
  description = models.TextField(max_length=LONG_STR_LEN)
  community = models.ForeignKey(Community, on_delete=models.CASCADE)
  members = models.ManyToManyField(UserProfile)
  permissions = models.ManyToManyField(Permission)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'user_groups'



class Data(models.Model):
	"""Instances keep track of a statistic from the admin"""
	description = models.CharField(max_length = LONG_STR_LEN)
	count =  models.PositiveSmallIntegerField(default=0)
	community = models.ForeignKey(Community, blank=False, 
    on_delete=models.SET_NULL, null=True)

	def __str__(self): 
		            
		return "%s: %s (Count: %d)" % (self.community, self.description, self.count)

	class Meta:
		verbose_name_plural = "Data"
		ordering = ('description','community')



class Statistic(models.Model):
	"""Instances keep track of a statistic from the admin"""
	description = models.CharField(max_length = LONG_STR_LEN)
	value =  models.PositiveSmallIntegerField(default=0)
	show_this_on_the_impact_page =  models.BooleanField(default=False)
	tag = models.CharField(max_length = LONG_STR_LEN, blank=True)
	symbol = models.CharField(max_length = LONG_STR_LEN, blank=True)
	community = models.ForeignKey(Community, blank=True,  
    on_delete=models.SET_NULL, null=True)

	def __str__(self):         
		return "%s (%d)" % (self.description, self.value)

	class Meta:
		verbose_name_plural = "Graph Statistics"
		ordering = ('tag', 'description','value')


class Graph(models.Model):
	"""Instances keep track of a statistic from the admin"""
	title = models.CharField(max_length = LONG_STR_LEN)
	statistic = models.ManyToManyField(Statistic)

	def __str__(self):   
		return self.title

	class Meta:
		verbose_name_plural = "Graphs"
		ordering = ('title',)

class SliderImage(models.Model):
	"""Model the represents the database for Images that will be 
  inserted into slide shows
  """
	title = models.CharField(max_length = LONG_STR_LEN, blank=True)
	description = models.CharField(max_length = LONG_STR_LEN, blank=True)
	image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True,blank=True)
	hyperlink = models.CharField(max_length = LONG_STR_LEN, blank=True)

	def __str__(self):             
		return self.title

	class Meta:
		verbose_name_plural = "Slider Images"

class Slider(models.Model):
	"""Model the represents the database for slide shows"""
	title = models.CharField(max_length = LONG_STR_LEN, blank=True)
	description = models.CharField(max_length = LONG_STR_LEN, blank=True)
	images = models.ManyToManyField(SliderImage)

	def __str__(self):             
		return self.title


class Menu(models.Model):
	"""Represents items on the menu bar (top-most bar on the webpage)"""
	position = models.PositiveSmallIntegerField(default=0)
	name = models.CharField(max_length=LONG_STR_LEN, blank = True)
	href = models.CharField(max_length=LONG_STR_LEN, blank = True)

	def __str__(self):              
		return "%d: %s" % (self.position, self.name)

	class Meta:
		ordering = ('position',)


class PageSection(models.Model):
	name = models.CharField(max_length=LONG_STR_LEN)
	content = models.TextField(max_length=LONG_STR_LEN, blank = True)
	image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True,blank=True)
	town = models.ManyToManyField(Community)
	page_associated = models.ForeignKey(Menu, on_delete=models.SET_NULL, null=True)

	def __str__(self):             
		return self.name


class Page(models.Model):
  name = models.CharField(max_length=LONG_STR_LEN)
  content = models.TextField(max_length=LONG_STR_LEN, blank = True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE)
  more_info = JSONField()

  def __str__(self):             
    return self.name

  class Meta:
    unique_together = ['name', 'community']


class Policy(models.Model):
  name = models.CharField(max_length=LONG_STR_LEN)
  content = models.TextField(max_length=LONG_STR_LEN, blank = True)
  communities = models.ManyToManyField(Community)
  more_info = JSONField()

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'massenergize_policies'


class Billing(models.Model):
  name = models.CharField(max_length=LONG_STR_LEN)
  content = models.TextField(max_length=LONG_STR_LEN, blank = True)
  more_info = JSONField()
  community = models.ForeignKey(Community, on_delete=models.CASCADE)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'billings'
