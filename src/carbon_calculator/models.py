from django.db import models
from django.contrib.postgres.fields import JSONField
from database.utils.constants import *
from database.models import UserProfile, Action, Media, CHOICES
# Create your models here.

NAME_STR_LEN = 25
class Action(models.Model):
    """
    A class representing a Carbon Calculator Action, as defined in the Carbon Calculator doc.
    This is different but related to the ME database Action, which can connect one-to-one with the CC Action

    Attributes
    ----------
    name : str  - unique string, which is the key which the front end will use
    description and helptext : descriptive strings
    average_points : typical impact in Tons CO2 per year, without any further input
    questions: ordered list of question names (from Question model) to ask to determine the parameters for a more detailed points estimate
    picture: a picture representing the action
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=SHORT_STR_LEN, null=True) #"Action short description"
    helptext = models.CharField(max_length=LONG_STR_LEN, null=True) #"This text explains what the action is about, in 20 words or less."
    average_points = models.PositiveIntegerField(default = 0)
    questions = JSONField(blank=True, null=True)    # list of questions by name
    picture = models.ForeignKey(Media, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='cc_action_picture')

    class Meta:
        db_table = 'cc_action'


CHOICE = 'C'
NUMBER = 'N'
TEXT = 'T'
RESPONSE_TYPES = [(CHOICE,'Choice'),(TEXT,'Text'),(NUMBER,'Number')]
class Question(models.Model):
    """
    A class representing a Carbon Calculator question, which are to determine the parameters used for Action points estimations defined in the Carbon Calculator doc.
    Questions may be used by multiple actions, and certain answers may make other questions not relevant (hence the 'skip' fields)

    Attributes
    ----------
    name : str  - unique string, which is the key which the front end will use
    category : organizational, not used for anything
    question_text : text of the question to be asked
    question_type : Choice for multiple choice (with up to 6 response options listed in subsequent fields)
                    Number for a numeric response
                    Text for a text response
    response_1, response_2 etc : valid responses for Choice questions.  If less than 6 valid responses, subsequent fields will be null
    skip_1, skip_2, etc: if this response makes some questions irrelevant, list of question names not to ask
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN, unique=True)
    category = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    question_text = models.CharField(max_length=SHORT_STR_LEN, blank=False)
    question_type = models.CharField(max_length=TINY_STR_LEN, choices=RESPONSE_TYPES, default=CHOICE)
    response_1 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_1 = JSONField(blank=True, null=True)
    response_2 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_2 = JSONField(blank=True, null=True)
    response_3 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_3 = JSONField(blank=True, null=True)
    response_4 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_4 = JSONField(blank=True, null=True)
    response_5 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_5 = JSONField(blank=True, null=True)
    response_6 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_6 = JSONField(blank=True, null=True)

    class Meta:
        db_table = 'cc_question'

class Station(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN, unique=True)
    description = models.CharField(max_length=SHORT_STR_LEN)
    actions = JSONField(blank=True, null=True)

    class Meta:
        db_table = 'cc_station'

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN, unique=True)
    shortname = models.CharField(max_length=TINY_STR_LEN, null=True)
    datetime = models.DateTimeField()
    location = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    stations = models.ForeignKey(Station, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='cc_action_picture')
    host_org = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    host_contact = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    host_email = models.EmailField()
    host_phone = models.CharField(max_length=TINY_STR_LEN, blank=True)
    host_url = models.URLField(blank=True)
    host_logo = models.ForeignKey(Media,on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='event_host_logo')
    sponsor_org = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    sponsor_url = models.URLField(blank=True)
    sponsor_logo = models.ForeignKey(Media,on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='event_sponsor_logo')

    class Meta:
        db_table = 'cc_event'

class ActionPoints(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    # get this from UserActionRel?  The status might change
    action_status = models.CharField(max_length=SHORT_STR_LEN, 
        choices = CHOICES["USER_ACTION_STATUS"].items(), 
        db_index=True, default='TODO')

    action = models.ForeignKey(Action, blank=True, null=True, on_delete=models.SET_NULL)
    # how to put in the questions and answers?

    points = models.PositiveIntegerField(default = 0, blank=True) 

    class Meta:
        db_table = 'cc_actionpoints'


# old models I'd like to delete and never see again

class CCAction(models.Model):
    #id = models.AutoField(primary_key=True)
    name = models.CharField(primary_key=True, max_length=SHORT_STR_LEN, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=SHORT_STR_LEN, null=True) #"Action short description"
    helptext = models.CharField(max_length=LONG_STR_LEN, null=True) #"This text explains what the action is about, in 20 words or less."
    average_points = models.PositiveIntegerField(default = 0)
    questions = JSONField(blank=True, null=True)    # list of questions by name
    #picture = models.ForeignKey(Media, on_delete=models.SET_NULL, 
    #    null=True, blank=True, related_name='ccaction_picture')

    #class Meta:
    #    db_table = 'cc_action'


class CCQuestion(models.Model):
    name = models.CharField(primary_key=True,max_length=SHORT_STR_LEN, blank=False)
    category = models.CharField(max_length=SHORT_STR_LEN, null=True)
    question_text = models.CharField(max_length=SHORT_STR_LEN, null=True)
    question_type = models.CharField(max_length=TINY_STR_LEN, choices=RESPONSE_TYPES, default=CHOICE)
    response_1 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_1 = JSONField(blank=True, null=True)
    response_2 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_2 = JSONField(blank=True, null=True)
    response_3 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_3 = JSONField(blank=True, null=True)
    response_4 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_4 = JSONField(blank=True, null=True)
    response_5 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_5 = JSONField(blank=True, null=True)
    response_6 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_6 = JSONField(blank=True, null=True)

class CCStation(models.Model):
    name = models.CharField(primary_key=True,max_length=SHORT_STR_LEN,blank=False)
    description = models.CharField(max_length=SHORT_STR_LEN, blank=False)
#    actions = models.ForeignKey(CCAction, on_delete=models.SET_NULL, 
#        null=True, blank=True, related_name='ccaction')
    actions = JSONField(blank=True, null=True)

class CCEvent(models.Model):
    name = models.CharField(primary_key=True,max_length=SHORT_STR_LEN, blank=False)
    shortname = models.CharField(max_length=TINY_STR_LEN, null=True)
    datetime = models.DateTimeField()
    location = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    stations = models.ForeignKey(CCStation, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='ccaction_picture')
    host_org = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    host_contact = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    host_email = models.EmailField()
    host_phone = models.CharField(max_length=TINY_STR_LEN, blank=True)
    host_url = models.URLField(blank=True)
    host_logo = models.ForeignKey(Media,on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='event_host_logo')
    sponsor_org = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    sponsor_url = models.URLField(blank=True)
    sponsor_logo = models.ForeignKey(Media,on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='event_sponsor_logo')

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

