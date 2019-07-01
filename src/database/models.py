from django.db import models
from django.contrib.postgres.fields import JSONField
from .utils.constants import *
from datetime import date, datetime
import django.contrib.auth.models as auth_models
from .utils import common

#TODO: enforce optional fields with blank=True
#TODO: add indexes to some models
#TODO: change some text field to html field?

CHOICES = common.json_loader('./database/raw_data/other/databaseFieldChoices.json')
ZIP_CODE_AND_STATES = common.json_loader('./database/raw_data/other/states.json')
API_URL = 'http://api.massenergize.org'


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
  name : SlugField
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
  name = models.CharField(max_length=SHORT_STR_LEN)
  status = models.CharField(
    max_length=TINY_STR_LEN, choices=CHOICES["GOAL_STATUS"].items())
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def get_status(self):
    return CHOICES["GOAL_STATUS"][self.status]

  def __str__(self):
    return self.name

  class Meta:
    db_table = 'goals'


class Role(models.Model):
  """
  A class used to represent  Role for users on the MassEnergize Platform

  Attributes
  ----------
  name : str
    name of the role
  """
  name = models.CharField(max_length=TINY_STR_LEN, 
    choices=CHOICES["ROLE_TYPES"].items(), 
    primary_key=True
  ) 
  description = models.TextField(max_length=LONG_STR_LEN, blank=True)


  def __str__(self):
    return CHOICES["ROLE_TYPES"][self.name] 

  class Meta:
    ordering = ('name',)
    db_table = 'roles'



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
    any another dynamic information we would like to store about this UserProfile 
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
  roles = models.ManyToManyField(Role) #TODO: if we have this do we need is_superadmin etc? also why not just one?  why many to many
  is_super_admin = models.BooleanField(default=False)
  is_community_admin = models.BooleanField(default=False)
  is_vendor = models.BooleanField(default=False)
  age_acknowledgment = models.BooleanField() #TODO: delete
  other_info = JSONField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

def __str__(self):
  return self.user_account.get_full_name()


class Meta:
  db_table = 'people' #TODO: change to user_profiles


class Team(models.Model):
  """
  A class used to represent a Team in a community

  Attributes
  ----------
  name : str
    name of the team
  description: str
    description of this team 
  admins:
    administrators for this team
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
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
  description = models.TextField(max_length=LONG_STR_LEN)
  admins = models.ManyToManyField(UserProfile, related_name='team_admins') 
  members = models.ManyToManyField(UserProfile, related_name='team_members') 
  goals = models.ManyToManyField(Goal) 
  logo = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_logo')
  banner = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_banner')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def is_admin(self, UserProfile):
    return self.admins.filter(id=UserProfile.id)

  def is_member(self, UserProfile):
    return self.members.filter(id=UserProfile.id)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'teams'


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
  name = models.CharField(max_length=SHORT_STR_LEN,unique=True)
  description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  service_location = models.ForeignKey(Location, on_delete=models.SET_NULL, 
    null=True, blank=True)
  image = models.ForeignKey(Media, blank=True, null=True, on_delete=models.SET_NULL)
  icon = models.CharField(max_length=SHORT_STR_LEN,blank=True)
  info = JSONField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):             
    return self.name

  class Meta:
    db_table = 'services'



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
    When this vendor was onboarded on the MassEnergize Platform for this community
  onboarding_contact:
    Which MassEnergize Staff/User onboarded this vendor
  verification_checklist:
    contains information about some steps and checks needed for due deligence 
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
  name = models.CharField(max_length=SHORT_STR_LEN,unique=True)
  description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  logo = models.ForeignKey(Media, blank=True, null=True, on_delete=models.SET_NULL, related_name='vender_logo')
  banner = models.ForeignKey(Media, blank=True, null=True, on_delete=models.SET_NULL, related_name='vendor_banner')
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
  verification_checklist = JSONField() 
  is_verified = models.BooleanField(default=False)
  more_info = JSONField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):             
    return self.name

  class Meta:
    db_table = 'vendors'


class ActionProperty(models.Model):
  """
  A class used to represent an Action property.

  Attributes
  ----------
  name : str
    name of the Vendor
  """
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
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
  """
  A class used to represent an Action Category.

  Attributes
  ----------
  name : str
    name of the Category
  """
  name = models.CharField(max_length = SHORT_STR_LEN, unique=True)
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
  """
  A class used to represent an Tag.  It is essentially a string that can be 
  used to describe or group items, actions, etc

  Attributes
  ----------
  name : str
    name of the Vendor
  """
  name = models.CharField(max_length = SHORT_STR_LEN, primary_key=True)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'tags'


class TagCollection(models.Model):
  """
  A class used to represent a collection of Tags.

  Attributes
  ----------
  name : str
    name of the Tag Collection
  """
  name = models.CharField(max_length = SHORT_STR_LEN, primary_key=True)
  tags = models.ManyToManyField(Tag)
  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'tag_collections'


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
  """
  A class used to represent an Event.

  Attributes
  ----------
  name : str
    name of the event
  """
  name  = models.CharField(max_length = SHORT_STR_LEN)
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
    return self.name

  class Meta:
    ordering = ('-start_date_and_time',)
    db_table = 'events'


class EventAttendees(models.Model):
  """
  A class used to represent events and attendees

  Attributes
  ----------
  attendee : str
    name of the Vendor
  status: str
    Tells if the attendee is just interested, RSVP'd or saved for later.
  event: int
    Foreign Key to event that the attendee is going to.
  """
  attendee =  models.ForeignKey(UserProfile,on_delete=models.CASCADE)
  event =  models.ForeignKey(Event,on_delete=models.CASCADE)
  status = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["EVENT_CHOICES"].items()
  )

  def __str__(self):
    return '%s | %s | %s' % (
      self.attendee, CHOICES["EVENT_CHOICES"][self.status], self.event)


class Permission(models.Model):

  """
   A class used to represent Permission(s) that are required by users to perform 
   any tasks on this platform.


  Attributes
  ----------
  name : str
    name of the Vendor
  """
  name = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=CHOICES["PERMISSION_TYPES"].items(), 
    primary_key=True
  ) 


  def __str__(self):
    return CHOICES["PERMISSION_TYPES"][self.name] 

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
  who = models.ForeignKey(Role,on_delete=models.CASCADE)
  can_do = models.ForeignKey(Permission, on_delete=models.CASCADE)
  #TODO: add with_what field?

  def __str__(self):
    return '(%s) can (%s)' % (self.who, self.can_do)

  class Meta:
    ordering = ('who',)
    db_table = 'user_permissions'


class Notification(models.Model):
  """
   A class used to represent Notifications served to user on MassEnergize


  Attributes
  ----------
  title : str
    title of the notification
  body: str
    body of the notification
  """
  title = models.CharField(max_length=SHORT_STR_LEN)
  body = models.CharField(max_length=LONG_STR_LEN, blank=True)

  def __str__(self):
    return self.title

  class Meta:
    ordering = ('title',)
    db_table = 'notifications'


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
  title = models.CharField(max_length=SHORT_STR_LEN)
  body = models.TextField(max_length=LONG_STR_LEN)
  is_approved = models.BooleanField(default=False)
  date = models.DateTimeField(default=datetime.now)
  file = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True)
  rank = models.PositiveSmallIntegerField(default=0)

  def __str__(self):        
    return "%d: %s" % (self.rank, self.name)

  class Meta:
    ordering = ('rank',)
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
    what they had to say about this action.  #TODO: do we need to create a secondary table
  """
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  real_estate_unit = models.ForeignKey(RealEstateUnit, on_delete=models.CASCADE)
  action = models.ForeignKey(Action, on_delete=models.CASCADE)
  vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, 
    null=True, blank=True)
  testimonial = models.ForeignKey(Testimonial, on_delete=models.SET_NULL, 
    null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return  "%s: %s" % (self.user, self.action)


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

  Attributes
  ----------
  name : str
    name of the page section
  info: JSON
    dynamic information goes in here
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


class Statistic(models.Model):
  """Instances keep track of a statistic from the admin

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
  name = models.CharField(max_length = SHORT_STR_LEN)
  value =  models.DecimalField(default=0.0, max_digits=10,decimal_places=10)
  symbol = models.CharField(max_length = LONG_STR_LEN, blank=True)

  community = models.ForeignKey(Community, blank=True,  
    on_delete=models.SET_NULL, null=True)
  info = JSONField()

  def __str__(self):         
    return "%s (%d)" % (self.name, self.value)

  class Meta:
    verbose_name_plural = "Graph Statistics"
    ordering = ('name','value')
    db_table = 'statistics'


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
  title = models.CharField(max_length = LONG_STR_LEN)
  graph_type = models.CharField(max_length=TINY_STR_LEN, 
    choices=CHOICES["GRAPH_TYPES"].items())
  data = JSONField()


  def __str__(self):   
    return self.title

  class Meta:
    verbose_name_plural = "Graphs"
    ordering = ('title',)



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
  title = models.CharField(max_length = LONG_STR_LEN, blank=True)
  subtitle = models.CharField(max_length = LONG_STR_LEN, blank=True)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True,blank=True)
  buttons = JSONField()

  def __str__(self):             
    return self.title

  class Meta:
    verbose_name_plural = "Slider Images"
    db_table = "slider_images"


class Slider(models.Model):
	"""Model the represents a model for a slider/carousel on the website
  
  Attributes
  ----------
  name : str
    name of the page section
  description: str
    a description of this slider
  info: JSON
    dynamic information goes in here
  """
	name = models.CharField(max_length = LONG_STR_LEN, blank=True)
	description = models.CharField(max_length = LONG_STR_LEN, blank=True)
	slides = models.ManyToManyField(SliderImage)

	def __str__(self):             
		return self.name


class Menu(models.Model):
  """Represents items on the menu/navigation bar (top-most bar on the webpage)
  Attributes
  ----------
  name : str
    name of the page section
  content: JSON
    the content is represented as a json
  """
  name = models.CharField(max_length=LONG_STR_LEN, blank = True)
  content = JSONField()

  def __str__(self):              
    return self.name

  class Meta:
    ordering = ('name',)



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
  name = models.CharField(max_length=LONG_STR_LEN)
  image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True,blank=True)
  info = JSONField()

  def __str__(self):             
    return self.name


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
  name = models.CharField(max_length=LONG_STR_LEN)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  community = models.ForeignKey(Community, on_delete=models.CASCADE)
  sections = models.ManyToManyField(PageSection)
  info = JSONField()


  def __str__(self):             
    return self.name

  class Meta:
    unique_together = ['name', 'community']


class Policy(models.Model):
  """
   A class used to represent a Legal Policy.  For instance the 
   Terms and Agreement Statement that users have to agree to during signup.


  Attributes
  ----------
  name : str
    name of the Legal Policy
  description: str
    the details of this policy
  communities_applied:
    how many communities this policy applies to.
  info: JSON
    dynamic information goes in here
  """
  name = models.CharField(max_length=LONG_STR_LEN)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  communities_applied = models.ManyToManyField(Community)
  more_info = JSONField()

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'massenergize_policies'


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
  name = models.CharField(max_length=LONG_STR_LEN)
  amount = models.DecimalField(default=0.0, decimal_places=4, max_digits = 10)
  description = models.TextField(max_length=LONG_STR_LEN, blank = True)
  start_date = models.DateTimeField(blank=True)
  end_date = models.DateTimeField(blank=True)
  more_info = JSONField()
  community = models.ForeignKey(Community, on_delete=models.CASCADE)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'billing_statements'
