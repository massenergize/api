from django.db import models
from django.contrib.postgres.fields import JSONField
from massenergize_portal_backend.utils.constants import *
from datetime import date, datetime
from authentication.models import *

# Create your models here.
class RealEstateUnit(models.Model):
  pass 


class Team(models.Model):
  pass 


class Goal(models.Model):
  pass 


class Neighbourhood(models.Model):
  pass 


class Partner(models.Model):
  pass 


class Community(models.Model):
  pass


class ActionProperty(models.Model):
	title = models.CharField(max_length=SHORT_STR_LEN, blank = True)
	short_description = models.CharField(max_length=LONG_STR_LEN, blank = True)
	community = models.ManyToManyField(Community)
	order_position = models.PositiveSmallIntegerField(default=0)

	def __str__(self):      
		return "%s: %s" % (self.order_position, self.name)

	class Meta:
		verbose_name_plural = "Properties"
		ordering = ('order_position',)


class ActionCategory(models.Model):
  title = models.CharField(max_length = SHORT_STR_LEN)
  icon = models.models.CharField(max_length = SHORT_STR_LEN, blank = True)
  community = models.ManyToManyField(Community)
  order_position = models.PositiveSmallIntegerField(default = 0)


  def __str__(self):              # __unicode__ on Python 2
    return "%d: %s" % (self.order_position, self.name)

  
  class Meta:
    verbose_name_plural = "Action Categories"
    ordering = ('order_position',)
    db_table = ('action_categories')


class Action(models.Model):
  title = models.CharField(max_length = SHORT_STR_LEN)
  full_description_and_next_steps = models.TextField(
    max_length = LONG_STR_LEN, 
    blank=True
  )
  partnership_information = HTMLField(max_length = LONG_STR_LEN, blank=True)
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

  choice = models.CharField(choices=list(EVENT_CHOICES.items()))
  user =  models.ForeignKey(UserProfile)
  event =  models.ForeignKey(Event)

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
    choices=list(TYPES.items()), 
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
    choices=list(TYPES.items()), 
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
  who = models.ForeignKey(Role)
  can_do = models.ForeignKey(Permission)
  #TODO: add with_what field?

  def __str__(self):
    return '(%s) can (%s)' % (self.who, self.can_do)

  class Meta:
    ordering = ('who',)
    db_table = 'policies'


class Notification(models.Model):
  title = models.CharField(max_lenth=SHORT_STR_LEN)
  body = models.CharField(max_length=LONG_STR_LEN, blank=True)

  def __str__(self):
    return self.title

  class Meta:
    ordering = ('title',)
    db_table = 'notifications'