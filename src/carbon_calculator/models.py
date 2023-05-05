from django.db import models
from django.forms.models import model_to_dict
from database.utils.constants import SHORT_STR_LEN, TINY_STR_LEN
from database.utils.common import  json_loader, get_json_if_not_none

# Create your models here.

NAME_STR_LEN = 40
MED_STR_LEN = 200
LONG_STR_LEN = 1000
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
    name = models.SlugField(max_length=SHORT_STR_LEN, blank=True) 
    file = models.FileField(upload_to='media/')
    is_deleted = models.BooleanField(default=False)

    def simple_json(self):
        return {
            "id": self.id,
            "url": self.file.url,
        }

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.file.name

    class Meta:
        db_table = "media_files_cc"

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN,unique=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    description = models.CharField(max_length=MED_STR_LEN, blank=True)
    
    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.name

    class Meta:
        db_table = 'categories_cc'

class Subcategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN,unique=True)
    is_deleted = models.BooleanField(default=False, blank=True) #Cascade??
    description = models.CharField(max_length=MED_STR_LEN, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.name

    class Meta:
        db_table = 'subcategories_cc'

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
    title = models.CharField(max_length=NAME_STR_LEN, blank=True)
    description = models.CharField(max_length=MED_STR_LEN, blank=True) #"Action short description"
    helptext = models.CharField(max_length=MED_STR_LEN, blank=True) #"This text explains what the action is about, in 20 words or less."
    average_points = models.PositiveIntegerField(default=0)
    questions = models.JSONField(blank=True)    # list of questions by name
    picture = models.ForeignKey(CarbonCalculatorMedia, on_delete=models.SET_NULL, null=True, related_name='cc_action_picture')
   
    old_category = models.CharField(max_length=NAME_STR_LEN, blank=True)

    category = models.ForeignKey(Category, on_delete= models.SET_NULL, null =True)
    sub_category = models.ForeignKey(Subcategory, on_delete = models.SET_NULL, null =True)


    def info(self):
        return model_to_dict(self, ['id', 'name', 'title', 'old_category', 'description', 'average_points'])

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self): 
        if self.category is None:
            s = self.old_category + ':' + self.name 
        else:
            s = self.category.name + ':' + self.name 
        return s

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
    skip_1 = models.JSONField(blank=True, null=True)
    response_2 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_2 = models.JSONField(blank=True, null=True)
    response_3 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_3 = models.JSONField(blank=True, null=True)
    response_4 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_4 = models.JSONField(blank=True, null=True)
    response_5 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_5 = models.JSONField(blank=True, null=True)
    response_6 = models.CharField(max_length=SHORT_STR_LEN, null=True)
    skip_6 = models.JSONField(blank=True, null=True)
    minimum_value = models.FloatField(null=True)
    maximum_value = models.FloatField(null=True)
    typical_value = models.FloatField(null=True)

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
    actions = models.JSONField(blank=True, null=True)

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.displayname

    class Meta:
        db_table = 'stations_cc'



class Group(models.Model):
    from database.models import UserProfile
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN,unique=True)
    displayname = models.CharField(max_length=NAME_STR_LEN,blank=True)
    description = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    member_list = models.ManyToManyField(UserProfile, related_name='group_members', blank=True) 
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

class Org(models.Model):
    """
    A class used to represent an organization

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
    name = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    contact = models.CharField(max_length=SHORT_STR_LEN,blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=TINY_STR_LEN, blank=True)
    about = models.CharField(max_length=LONG_STR_LEN, blank=True)
    url = models.URLField(blank=True)
    logo = models.ForeignKey(CarbonCalculatorMedia,on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='event_host_logo')

    def simple_json(self):
        return {
            "name": self.name,
            "contact": self.contact,
            "email": self.email,
            "phone": self.phone,
            "about": self.about,
            "url":self.url,
            "logo":get_json_if_not_none(self.logo)
        }


    def full_json(self):
        return self.simple_json()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'organization_cc' 

class Event(models.Model):
    from database.models import UserProfile
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=NAME_STR_LEN,unique=True)
    displayname = models.CharField(max_length=NAME_STR_LEN,blank=True)
    datetime = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=SHORT_STR_LEN,blank=True)
#    stations = models.ForeignKey(Station, on_delete=models.SET_NULL, 
#        null=True, blank=True, related_name='cc_station_picture')
    stationslist = models.JSONField(null=True, blank=True)
    groups = models.ManyToManyField(Group,blank=True)
    host_org = models.ManyToManyField(Org,blank=True,related_name='host_orgs')
    sponsor_org = models.ManyToManyField(Org,blank=True,related_name='sponsor_orgs')
#   updated 4/24/20
#   for a given event, campaign or purpose (platform default or community sites)
    visible = models.BooleanField(default=True)
    event_tag = models.CharField(max_length=TINY_STR_LEN,blank=True)
    #attendees = models.ManyToManyField(CalcUser, blank=True)
    attendees = models.ManyToManyField(UserProfile, blank=True)

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
    from database.models import UserProfile
    id = models.AutoField(primary_key=True)
    #user = models.ForeignKey(CalcUser, blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)

    created_date = models.DateTimeField(auto_now_add=True)
#
    #action = models.ForeignKey(Action, blank=True, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=NAME_STR_LEN, blank=True)

#    the questions and answers
    choices = models.JSONField(blank=True)

    #next two fields added 11/15/20
    action_date = models.DateTimeField(auto_now_add=True, null=True)
    # 'pledged', 'todo', 'done'
    action_status = models.CharField(max_length=NAME_STR_LEN,blank=True)
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
    valid_date = models.DateField(null=True)
    value = models.FloatField(default=0.0)
    reference = models.CharField(max_length=MED_STR_LEN)
    updated = models.DateTimeField(auto_now_add=True)

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self):
        message = "%s : %s = %.3f" % (self.locality,self.variable, self.value)
        if self.valid_date:
            message += "-" + str(self.valid_date)
        return message

    class Meta:
        db_table = 'defaults_cc'

