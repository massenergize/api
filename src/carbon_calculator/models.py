from django.db import models
from django.forms.models import model_to_dict
from database.utils.constants import SHORT_STR_LEN, TINY_STR_LEN
from database.utils.common import  json_loader

# Create your models here.

NAME_STR_LEN = 40
MED_STR_LEN = 200
LONG_STR_LEN = 1000
CHOICES = json_loader('./database/raw_data/other/databaseFieldChoices.json')

class Version(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.CharField(max_length=TINY_STR_LEN, blank=True, null=True)
    note = models.CharField(max_length=MED_STR_LEN, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def simple_json(self):
        return model_to_dict(self)
    
    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return self.version + " - " + str(self.updated_on)

    class Meta:
        db_table = "version_cc"


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
    name = models.CharField(max_length=NAME_STR_LEN)
    is_deleted = models.BooleanField(default=False, blank=True) #Cascade??
    description = models.CharField(max_length=MED_STR_LEN, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def simple_json(self):
        data =  model_to_dict(self,exclude=["category"])
        data["category"] = self.category.simple_json() if self.category else None
        return data

    def full_json(self):
        return self.simple_json()

    def __str__(self):      
        return str(self.category.name) + ": " + str(self.name)

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

    # for the possibility of deleting actions
    # is_deleted = models.BooleanField(default=False)
    
    def info(self):
        return model_to_dict(self, ['id', 'name', 'title', 'category', 'description', 'average_points'])

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    def __str__(self): 
        if self.category is None:
            s = self.name 
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

