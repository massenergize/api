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

class Location(models.Model):
  LOCATION_TYPES = [
    ('S', 'STATE ONLY'),
    ('Z', 'ZIP CODE ONLY'),
    ('C', 'CITY ONLY'),
    ('F', 'FULL ADDRESS')
  ]
  name = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  type = models.CharField(max_length=TINY_STR_LEN, choices=LOCATION_TYPES)
  street = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  unit_number = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  zipcode = models.CharField(max_length=SHORT_STR_LEN, blank=True)
  city = models.CharField(max_length=SHORT_STR_LEN, blank=True) 
  state = models.CharField(
    max_length=SHORT_STR_LEN, 
    choices = common.json_loader('./database/raw_data/other/states.json').items(),
    blank=True
  )
  more_info = JSONField()

  def __str__(self):
    return "%s, %s" % (self.type, self.name)


class Community(models.Model):
  name = models.CharField(max_length=SHORT_STR_LEN)
  subdomain = models.CharField(max_length=SHORT_STR_LEN, unique=True)
  community_admin_info = JSONField() #name, email, phone
  about_you = models.TextField(max_length=LONG_STR_LEN)
  logo = models.FileField(upload_to='community/logos', blank=True)
  banner = models.FileField(upload_to='community/banners', blank=True)
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
  REAL_ESTATE_TYPES = {
    'C': 'Commercial', 
    'R': 'Residential'
  }

  unit_type =  models.CharField(
    max_length=TINY_STR_LEN, 
    choices=list(REAL_ESTATE_TYPES.items())
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
  GOAL_STATUS = {
    'I': 'In Progress',
    'N': 'Not Started',
    'C': 'Completed'
  }

  title = models.CharField(max_length=SHORT_STR_LEN)
  status = models.CharField(
    max_length=TINY_STR_LEN, choices=list(GOAL_STATUS.items())
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def get_status(self):
    return GOAL_STATUS[self.status]

  def __str__(self):
    return self.title

  class Meta:
    db_table = 'goals'


class UserProfile(models.Model):
  user_account = models.ForeignKey(auth_models.User, on_delete=models.CASCADE, null=True)
  address = models.ForeignKey(RealEstateUnit, on_delete=models.SET_NULL, null=True) #TODO: delete
  real_estate_units = models.ManyToManyField(RealEstateUnit, related_name='user_real_estate_units')
  goals = models.ManyToManyField(Goal)
  communities = models.ManyToManyField(Community)
  is_super_admin = models.BooleanField()
  is_community_admin = models.BooleanField()
  other_info = JSONField()
  age_acknowledgment = models.BooleanField() #TODO: delete
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
  service_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
  info = JSONField()


  def __str__(self):             
    return self.name

  class Meta:
    db_table = 'services'



class Vendor(models.Model):
  SERVICE_AREAS = [
    ('N', 'National'),
    ('S', 'StateWide'),
    ('C', 'County'),
    ('T', 'Town')
  ]
  PROPERTIES_SERVICED = [
    ('R', 'Residential'),
    ('C', 'Commercial')
  ]
  name = models.CharField(max_length=SHORT_STR_LEN,unique=True)
  address = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL)
  key_contact = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL, related_name='key_contact')
  service_area = models.CharField(max_length=TINY_STR_LEN, choices=SERVICE_AREAS)
  services = models.ManyToManyField(Service)
  properties_serviced = models.CharField(max_length=TINY_STR_LEN, choices=PROPERTIES_SERVICED)
  onboarding_date = models.DateTimeField(default=datetime.now)
  onboarding_contact = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL, related_name='onboarding_contact')
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


class SuperTag(models.Model):
  value = models.CharField(max_length = SHORT_STR_LEN, primary_key=True)
  tags = models.ManyToManyField(Tag, related_name='supertags_to_tags')
  def __str__(self):
    return self.value

  class Meta:
    ordering = ('value',)
    db_table = 'supertags'


class Action(models.Model):
  title = models.CharField(max_length = SHORT_STR_LEN)
  is_template_action = models.BooleanField(default=False)
  steps_to_take = models.TextField(max_length = LONG_STR_LEN, blank=True)
  partnership_information = models.TextField(max_length = LONG_STR_LEN, blank=True)

  #TODO: needed?  Don't the tags rather have super tags
  super_tags = models.ManyToManyField(SuperTag, related_name='action_supertags')  
  tags = models.ManyToManyField(Tag, related_name='action_tags')

  #some actions are constrained to only a specific geographic area.
  geographic_focus = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)

  icon = models.CharField(max_length = SHORT_STR_LEN)
  image = models.ImageField(upload_to='photos/actions')
  
  properties = models.ManyToManyField(ActionProperty)
  vendors = models.ManyToManyField(Vendor)
  community = models.ForeignKey(Community, on_delete=models.SET_NULL)
  category = models.ManyToManyField(ActionCategory) 

  #the order in which it should appear relative to its peers
  rank = models.PositiveSmallIntegerField(default = 0) 

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self): 
    return self.title


  class Meta:
    ordering = ('rank', 'order_position','title') 
    db_table = 'actions'
    unique_together = [['title', 'community']]


class Event(models.Model):
  title  = models.CharField(max_length = SHORT_STR_LEN)
  description = models.TextField(max_length = LONG_STR_LEN)
  start_date_and_time  = models.DateTimeField(default=datetime.now)
  end_date_and_time  = models.DateTimeField(default=datetime.now)
  location = models.CharField(max_length = SHORT_STR_LEN, blank=True)
  tags = models.ManyToManyField(Tag)
  image = models.ImageField(upload_to='images/events', blank=True)
  archive =  models.BooleanField(default=False)

  def __str__(self):             
    return self.title

  class Meta:
    ordering = ('-start_date_and_time',)
    db_table = 'events'


class EventUserRel(models.Model):
  EVENT_CHOICES = {
    'I': 'Interested',
    'R': 'RSVP',
    'S': 'Save for Later'
  }

  choice = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=list(EVENT_CHOICES.items())
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
  PERMISSION_TYPES = {
    'A': 'Approve', 
    'C': 'Create', 
    'E': 'Edit',
    'F': 'Fork',
    'V': 'View'
  }

  permission_type = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=list(PERMISSION_TYPES.items()), 
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
    return 'Can: %s' %  PERMISSION_TYPES[self.permission_type] 

  class Meta:
    ordering = ('permission_type',)
    db_table = 'permissions'

    

class Role(models.Model):
  ROLE_TYPES = {
    'C': 'Community Admin', 
    'S': 'SuperAdmin', 
    'T': 'Team Admin',
    'U': 'Default User',
    'V': 'Vendor Admin',
  }

  role_type = models.CharField(
    max_length=TINY_STR_LEN, 
    choices=list(ROLE_TYPES.items()), 
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
    return 'Is: %s' % ROLE_TYPES[self.role_type] 

  class Meta:
    ordering = ('role_type',)
    db_table = 'roles'


class Policy(models.Model):
  who = models.ForeignKey(Role,on_delete=models.CASCADE)
  can_do = models.ForeignKey(Permission, on_delete=models.CASCADE)
  #TODO: add with_what field?

  def __str__(self):
    return '(%s) can (%s)' % (self.who, self.can_do)

  class Meta:
    ordering = ('who',)
    db_table = 'policies'


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
  file = models.FileField(upload_to='testimonials/', blank=True)

  def __str__(self):        
    return "%d: %s" % (self.rank, self.name)

  class Meta:
    ordering = ('rank',)
    db_table = 'testimonials'

  
class ActionTaken(models.Model):
  user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  real_estate_unit = models.ForeignKey(RealEstateUnit, on_delete=models.CASCADE)
  action = models.ForeignKey(Action, on_delete=models.CASCADE)
  vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
  testimonial = models.ForeignKey(Testimonial, on_delete=models.SET_NULL, null=True, blank=True)
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