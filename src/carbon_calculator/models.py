from django.db import models
from django.contrib.postgres.fields import JSONField
from django.forms.models import model_to_dict
from database.utils.constants import SHORT_STR_LEN, TINY_STR_LEN
from database.utils.common import  json_loader
# Create your models here.

NAME_STR_LEN = 40
MED_STR_LEN = 200
CHOICES = json_loader('./database/raw_data/other/databaseFieldChoices.json')

class CarbonCalculatorMedia(models.Model):
    """
    A class used to represent any CarbonCalculatorMedia that is uploaded to this website

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
    file = models.FileField(upload_to='cc_media/')
    is_deleted = models.BooleanField(default=False)

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.file.name

    class Meta:
        db_table = "media_files_cc"


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
    description = models.CharField(max_length=SHORT_STR_LEN, blank=True) #"Action short description"
    helptext = models.CharField(max_length=MED_STR_LEN, blank=True) #"This text explains what the action is about, in 20 words or less."
    average_points = models.PositiveIntegerField(default=0)
    questions = JSONField(blank=True)    # list of questions by name
    picture = models.ForeignKey(CarbonCalculatorMedia, on_delete=models.SET_NULL, null=True, related_name='cc_action_picture')

    def info(self):
        return model_to_dict(self, ['id', 'name', 'description', 'average_points'])

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.name

    class Meta:
        db_table = 'actions_cc'


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
    CHOICE = 'C'
    NUMBER = 'N'
    TEXT = 'T'
    RESPONSE_TYPES = [(CHOICE,'Choice'),(TEXT,'Text'),(NUMBER,'Number')]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN, unique=True)
    category = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    question_text = models.CharField(max_length=MED_STR_LEN, blank=False)
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

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.name

    class Meta:
        db_table = 'questions_cc'

class Station(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN, unique=True)
    displayname = models.CharField(max_length=NAME_STR_LEN,blank=True)
    description = models.CharField(max_length=SHORT_STR_LEN)
    icon = models.ForeignKey(CarbonCalculatorMedia, on_delete=models.SET_NULL, null=True, related_name='cc_station_icon')
    actions = JSONField(blank=True, null=True)

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.displayname

    class Meta:
        db_table = 'stations_cc'



class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN,unique=True)
    displayname = models.CharField(max_length=NAME_STR_LEN,blank=True)
    description = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    members = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    savings = models.DecimalField(default=0.0,max_digits=10,decimal_places=2)
    
    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.displayname

    class Meta:
        db_table = 'groups_cc'


class CalcUser(models.Model):
    """
    A class used to represent a Calculator User

    Note: Authentication is handled by firebase so we just need emails

    Attributes
    ----------
    email : str
      email of the user.  Should be unique.
      created_at: DateTime
      The date and time that this goal was added 
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this goal

    """
    id = models.AutoField(primary_key=True)
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    first_name = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    last_name = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    email = models.EmailField(max_length=SHORT_STR_LEN, 
      unique=True, db_index=True)
    locality = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    groups = models.ManyToManyField(Group, blank=True)
    minimum_age = models.BooleanField(default=False, blank=True)
    accepts_terms_and_conditions = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #updated 12/1
    points = models.IntegerField(default = 0) 
    cost = models.IntegerField(default = 0)
    savings = models.IntegerField(default = 0)

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):
        return self.email
#
    class Meta:
        db_table = 'user_profiles_cc' 

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN,unique=True)
    displayname = models.CharField(max_length=NAME_STR_LEN,blank=True)
    datetime = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=SHORT_STR_LEN,blank=True)
#    stations = models.ForeignKey(Station, on_delete=models.SET_NULL, 
#        null=True, blank=True, related_name='cc_station_picture')
    stationslist = JSONField(null=True, blank=True)
    groups = models.ManyToManyField(Group,blank=True)
    host_org = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    host_contact = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    host_email = models.EmailField()
    host_phone = models.CharField(max_length=TINY_STR_LEN, blank=True)
    host_url = models.URLField(blank=True)
    host_logo = models.ForeignKey(CarbonCalculatorMedia,on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='event_host_logo')
    sponsor_org = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    sponsor_url = models.URLField(blank=True)
    sponsor_logo = models.ForeignKey(CarbonCalculatorMedia,on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='event_sponsor_logo')
#   updated 4/24/20
#   for a given event, campaign or purpose (platform default or community sites)
    event_tag = models.CharField(max_length=TINY_STR_LEN,blank=True)
    attendees = models.ManyToManyField(CalcUser, blank=True)

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.displayname

    class Meta:
        db_table = 'events_cc'


class ActionPoints(models.Model):
    """
    Class to record choices made for actions - first from the Event Calculator and eventually from  
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CalcUser, blank=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
#
    #action = models.ForeignKey(Action, blank=True, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=NAME_STR_LEN, blank=True)
    choices = JSONField(blank=True)
#    # how to put in the questions and answers?
#
    points = models.IntegerField(default = 0) 
    cost = models.IntegerField(default = 0)
    savings = models.IntegerField(default = 0)

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()
#        
    def __str__(self):      
        return "%s-%s-(%s)" % (self.action, self.user, self.created_date)

    class Meta:
        db_table = 'action_points_cc'
#
#
class CalcDefault(models.Model):
    """
    Class to keep track of calculator assumptions by locality

    """
    id = models.AutoField(primary_key=True)
    variable = models.CharField(max_length=NAME_STR_LEN,blank=False)
    locality = models.CharField(max_length=NAME_STR_LEN)
    value = models.FloatField(default=0.0)
    reference = models.CharField(max_length=MED_STR_LEN)
    updated = models.DateTimeField(auto_now_add=True)

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return "%s : %s = %.3f" % (self.locality,self.variable, self.value)

    class Meta:
        db_table = 'defaults_cc'

