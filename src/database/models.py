from django.db import models

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


class Action(models.Model):
  pass 


class Tag(models.Model):
  pass 


class Items(models.Model):
  pass 


class Event(models.Model):
  pass 


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
    return 'Can: %s' % TYPES[self.permission_type] 

  class Meta:
    ordering = ('permtype',)
    db_table = "permissions"

    

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
    return 'Can: %s' % ROLE_TYPES[self.role_type] 

  class Meta:
    ordering = ('role_type',)
    db_table = "roles"


class Policy(models.Model):
  pass 


class Notification(models.Model):
  pass
