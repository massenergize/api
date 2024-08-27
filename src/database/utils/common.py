"""
This file contains utility functions that come in handy for processing and 
retrieving data
"""
import base64
import hashlib
import json
from django.forms.models import model_to_dict
from collections.abc import Iterable
from _main_.settings import AWS_S3_REGION_NAME, AWS_STORAGE_BUCKET_NAME
from _main_.utils.massenergize_logger import log
import boto3

s3 = boto3.client('s3', region_name=AWS_S3_REGION_NAME)


def get_images_in_sequence(images,sequence): 
  if not sequence: return images  
  if not images: return []
  arr = []
  for id in sequence: 
    img = list(filter(lambda image: str(image.id) == id,images))
    if len(img): 
      arr.append(img[0].simple_json())
  return arr


def json_loader(file) -> dict:
  """
  Returns json data given a valid filepath.  Returns {} if error occurs
  """
  try:
    with open(file) as my_file:
      data = my_file.read()
    return json.loads(data)
  except Exception as e:
    log.exception(e)
    
    return error_msg("The JSON file you specified does not exist")

def error_msg(msg=None):
  return {
    "success": False,
    "msg": msg if msg else 'The data you were looking for does not exist'
  }


def retrieve_object(model, args, full_json=False) -> dict:
  """
  Retrieves one object of a database model/table given the filter categories.

  Arguments
  -----------
  model: models.Model
    The database model/table to retrieve from
  args: dict
    A dictionary with the filter arguments/params
  full_json: boolean
    True if we want to retrieve the full json for each object or not
  """
  obj = model.objects.filter(**args).first()
  if obj:
    return obj.full_json() if full_json else obj.simple_json()
  return error_msg('No object found matching the criteria given')



def retrieve_all_objects(model, args, full_json=False) -> list:
  """
  Filters for all objects in a database model that fits a criterion

  Arguments
  -----------
  model: models.Model
    The database model/table to retrieve from
  args: dict
    A dictionary with the filter arguments/params
  full_json: boolean
    True if we want to retrieve the full json for each object or not
  """
  objects = model.objects.filter(**args)
  return [
    (i.full_json() if full_json else i.simple_json()) for i in objects
  ]

def convert_to_json(data, full_json=False):
  """
  Serializes an object into a json to be sent over-the-wire 
  """
  if not data and not isinstance(data, Iterable):
    return None
  elif isinstance(data, dict):
    return data 
  elif isinstance(data, Iterable):
    return  [
      (i.full_json() if full_json else i.simple_json()) for i in data
    ]
  else:
    return data.full_json()
    # serialized_object = serializers.serialize("json", objects)
    # result = json.loads(serialized_object)[0]["fields"]
    # result["id"] = json.loads(serialized_object)[0]["pk"]
    # return result


def get_json_if_not_none(obj, full_json=False) -> dict:
  """
  Takes an object and returns the json/serialized form of the obj if it is 
  not None.
  """
  if obj:
    return obj.simple_json() if not full_json else obj.full_json()
  return None

def get_summary_info(obj) -> dict:
  """
  Takes an object and returns the json/serialized form of the obj if it is 
  not None.
  """
  try:
    if obj:
      return obj.info()
    return None
  except Exception as e:
    log.exception(e)
    
    return {'id': obj.pk}


def ensure_required_fields(required_fields, args):
  errors = []
  for f in required_fields:
    if f not in args:
      errors.append(f"You are missing a required field: {f}")
  return errors

def rename_filter_args(args, pairs):
  for (old_key, new_key) in pairs:
    if old_key in args:
      args[new_key] = args.pop(old_key)
  return args

def get_request_contents(request):
  if request.method == 'POST':
    try:
      if not request.POST:
        return json.loads(request.body.decode('utf-8'))
      else:
        tmp = request.POST.dict()
        if(request.FILES):
          for i in request.FILES.dict():
            tmp[i] = request.FILES[i]
        return tmp
    except:
      return request.POST.dict()
  elif request.method == 'GET':
    return request.GET.dict()

  elif request.method == 'DELETE':
    try:
      return json.loads(request.body.decode('utf-8'))
    except Exception as e:
      log.exception(e)
      return {}


def read_image_from_s3(key, bucket_name =None):
  bucket_name = bucket_name or  AWS_STORAGE_BUCKET_NAME
  # Retrieve the image from the S3 bucket
  response = s3.get_object(Bucket=bucket_name, Key=key)
  # Get the image data as bytes
  image_data = response['Body'].read()
  # Encode the image data to base64
  base64_image = base64.b64encode(image_data).decode('utf-8') 
  data = f'data:{response["ContentType"]};base64,{base64_image}'

  return data


def make_hash_from_file(file_data): 
  """
    Given data from a file that has been read, it
    Returns: 
    A hash representation of the file as string
  """
  if not file_data: 
    return None 
  hash_object = hashlib.sha256()
  hash_object.update(file_data)
  return hash_object.hexdigest()

s3 = boto3.client("s3", region_name=AWS_S3_REGION_NAME)
def calculate_hash_for_bucket_item(key, bucket=AWS_STORAGE_BUCKET_NAME):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response["Body"].read()
        return make_hash_from_file(image_data)
    except Exception as e:
        print("........................................")
        print(f"Error calculating hash for {key}: {e}")
        print("........................................")
        return None
    
def get_image_size_from_bucket(key,bucket=AWS_STORAGE_BUCKET_NAME): 
  try:
      response = s3.get_object(Bucket=bucket, Key=key)
      size = response["ContentLength"]
      return size or 0
  except Exception as e:
      print("Error retrieving image size...")
