from django.db import models
from django.contrib.postgres.fields import JSONField
from database.utils.constants import *
from database.models import UserProfile, Action, CHOICES
# Create your models here.

class CCAction(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=SHORT_STR_LEN, null=True) #"Action short description"
    helptext = models.CharField(max_length=LONG_STR_LEN, null=True) #"This text explains what the action is about, in 20 words or less."
    questions = JSONField(blank=True, null=True)    # question with list of valid responses.
    average_points = models.PositiveIntegerField(default = 0, blank=True)

class CCActionPoints(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    # get this from UserActionRel?  The status might change
    action_status = models.CharField(max_length=SHORT_STR_LEN, 
        choices = CHOICES["USER_ACTION_STATUS"].items(), 
        db_index=True, default='TODO')

    action = models.ForeignKey(CCAction, blank=True, null=True, on_delete=models.SET_NULL)
    # how to put in the questions and answers?

    points = models.PositiveIntegerField(default = 0, blank=True) 

