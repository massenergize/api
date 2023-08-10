import json, os
import django.db.models.base as Base
import inspect
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def load_json(path):
    """
    Loads the json file in the given path.

    Precondition:
    path: is a string of a valid json path.
    """
    with open(path) as file:
        return json.load(file)
    return {}


def load_text_contents(path) -> str:
    data = {}
    with open(path) as f:
        data = f.read()

    return data


def get_all_models(models):
    """
    This function takes a Django models.py class and extracts all the models
    defined in there and returns them as a list.
    """
    return [
        m[1]
        for m in inspect.getmembers(models, inspect.isclass)
        if (isinstance(m[1], Base.ModelBase))
    ]


def get_models_and_field_types(models):
    """
    This method take a models.py class and makes a dictionary of all the models
    mapping them to their fields in groups.

    eg. {
          model1: {"m2m": {...}, "fk": {....}, "other":{....},
            "required_fields":{.....}}
          ....
        }
        Hence for each model, we collect and group all the many to many fields
        as well as foreignkeys as well as get which fields are required
    """
    all_models = get_all_models(models)
    result = {}
    for m in all_models:
        result[m] = {
            "m2m": set(),
            "fk": set(),
            "other": set(),
            "required_fields": set(),
            "all_fields": set(),
        }
        for f in m._meta.get_fields():
            result[m]["all_fields"].add(f.name)
            if isinstance(f, ManyToManyField):
                result[m]["m2m"].add(f.name)
            elif isinstance(f, ForeignKey):
                result[m]["fk"].add(f.name)
            else:
                result[m]["other"].add(f.name)

            if hasattr(f, "blank") and f.blank == False:
                result[m]["required_fields"].add(f.name)
    return result


def strip_website(url: str) -> str:
    if not url:
        return None
    url = url.replace("http://", "")
    url = url.replace("https://", "")
    url = url.split("/")[0]  # deal with trailing spaces
    return url.strip()


class Console:
    @staticmethod
    def log(key, *content):
        """
        A simple class that manages logging to terminal in a way that logs are
        easier to find
        """
        print(f"=================={key or'START LOG'}================")
        for c in content:
            if isinstance(c,dict) or isinstance(c,list):
                item = json.dumps(c, indent=4)
                print(item)
            else:
                print(c)
            print("..................................................")
        print(f"==================END LOG================")

    @staticmethod
    def underline(text=None):
        if text:
            print(text)
            print(Console.makeLine(len(text)))
            return
        print("-------------------------------")

    @staticmethod
    def makeLine(len):
        string = ""
        for a in range(len):
            string += "-"
        return string

    @staticmethod
    def header(text):
        text = text or "Logging..."
        print(Console.makeLine(len(text)))
        print(text)
        print(Console.makeLine(len(text)))


def is_test_mode():
    return os.environ.get("DJANGO_ENV", "").lower() == "test"


def is_not_null(data):
    if data == "null" or data == None:
        return False
    return True


def is_url_valid(url):
    validate = URLValidator()
    try:
        validate(url)
    except ValidationError:
        return False
    return True

