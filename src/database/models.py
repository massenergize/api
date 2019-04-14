from django.db import models
from django.contrib.postgres.fields import JSONField
from massenergize_portal_backend.utils.constants import *
from datetime import date, datetime
import django.contrib.auth.models as auth_models

# Create your models here.
class Community(models.Model):
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)

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
      max_length=SHORT_STR_LEN, 
      choices=list(REAL_ESTATE_TYPES.items())
    )
    street = models.CharField(max_length=SHORT_STR_LEN)
    unit_number = models.CharField(max_length=SHORT_STR_LEN)
    zipcode = models.CharField(max_length=SHORT_STR_LEN)
    city = models.CharField(max_length=SHORT_STR_LEN) 
    state = models.CharField(
      max_length=SHORT_STR_LEN, 
      choices = list(USA_STATES.items())
    )

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
    max_length=SHORT_STR_LEN, choices=list(GOAL_STATUS.items())
  )

  def get_status(self):
    return GOAL_STATUS[self.status]

  def __str__(self):
    return self.title

  class Meta:
    db_table = 'goals'


class UserProfile(models.Model):
  user_account = models.ForeignKey(
    auth_models.User, on_delete=models.CASCADE, null=True
  )
  address = models.ForeignKey(
    RealEstateUnit, on_delete=models.SET_NULL, null=True
  )
  goals = models.ManyToManyField(Goal)
  community = models.ForeignKey(Community,on_delete=models.SET_NULL, null=True)
  age_acknowledgment = models.BooleanField()
  other_info = JSONField()

def __str__(self):
  return self.get_full_name()

class Meta:
  db_table = 'people'


class Team(models.Model):
  name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
  description = models.TextField(max_length=LONG_STR_LEN)
  admins = models.ManyToManyField(UserProfile, related_name='team_admins') 
  members = models.ManyToManyField(UserProfile, related_name='team_members') 
  goals = models.ManyToManyField(Goal) 

  def is_admin(self, UserProfile):
    return self.members.filter(id=UserProfile.id)

  def is_member(self, UserProfile):
    return self.members.filter(id=UserProfile.id)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ('name',)
    db_table = 'teams'


class Partner(models.Model):
  name = models.CharField(max_length=SHORT_STR_LEN,unique=True)
  description = models.CharField(max_length=LONG_STR_LEN, blank = True)
  community = models.ManyToManyField(Community)
  info = JSONField()

  def __str__(self):             
    return self.name

  class Meta:
    db_table = 'partners'


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


class Action(models.Model):
  title = models.CharField(max_length = SHORT_STR_LEN, unique=True)
  full_description_and_next_steps = models.TextField(
    max_length = LONG_STR_LEN,
    blank=True
  )
  partnership_information = models.TextField(
    max_length = LONG_STR_LEN, blank=True
    )
  category = models.ManyToManyField(ActionCategory)
  properties = models.ManyToManyField(ActionProperty)
  partners = models.ManyToManyField(Partner)
  community = models.ManyToManyField(Community)
  order_position = models.PositiveSmallIntegerField(default = 0)


  def __str__(self): 
    return self.title

  class Meta:
    ordering = ('order_position','title') 
    db_table = 'actions'


class Tag(models.Model):
  value = models.CharField(max_length = SHORT_STR_LEN, primary_key=True)

  def __str__(self):
    return self.value

  class Meta:
    ordering = ('value',)
    db_table = 'tags'

class Event(models.Model):
  title  = models.CharField(max_length = SHORT_STR_LEN)
  description = models.TextField(max_length = LONG_STR_LEN)
  start_date_and_time  = models.DateTimeField(default=datetime.now)
  end_date_and_time  = models.DateTimeField(default=datetime.now)
  location = models.CharField(max_length = SHORT_STR_LEN)
  tags = models.ManyToManyField(Tag)
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
    max_length=SHORT_STR_LEN, 
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
    max_length=SHORT_STR_LEN, 
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
    'D': 'Default User',
    'P': 'Partner Admin',
    'N': 'Neighborhood Admin', 
    'R': 'Unit Admin', 
    'S': 'SuperAdmin', 
    'T': 'Team Admin',
  }

  role_type = models.CharField(
    max_length=SHORT_STR_LEN, 
    choices=list(ROLE_TYPES.items()), 
    primary_key=True
  ) 


  def is_default_user(self):
    return self.role_type == 'D'


  def is_super_admin(self):
    return self.role_type == 'S'


  def is_neighbourhood_admin(self):
    return self.role_type == 'N'

  
  def is_team_admin(self):
    return self.role_type == 'T'

  
  def is_unit_admin(self):
    return self.role_type == 'R'

  
  def is_partner_admin(self):
    return self.role_type == 'P'

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