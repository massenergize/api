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
    db_table = "permissions_for_users"

    

class Role(models.Model):
  pass 


class Policy(models.Model):
  pass 


class Notification(models.Model):
  pass
