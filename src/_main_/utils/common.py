import json 
from querystring_parser import parser
from _main_.utils.massenergize_errors import CustomMassenergizeError
import pytz
from django.utils import timezone
from datetime import datetime
#import cv2
from sentry_sdk import capture_message

def get_request_contents(request):
  try:
    if request.method != 'POST' :
      return request.GET.dict()

    args = {}
    if request.content_type == 'application/x-www-form-urlencoded':
      args = parser.parse(request.POST.urlencode())
    elif request.content_type == 'multipart/form-data':
      args = request.POST.dict()
      if(request.FILES):
        for i in request.FILES.dict():
          args[i] = request.FILES[i]
    else:
      args = request.POST.dict()
    
    return args

  except Exception as e:    
    capture_message(str(e), level="error")
    return {}

def parse_list(d):
  try:
    tmp = []
    if isinstance(d, str):
      tmp = d.strip().split(',') if d else []
    elif isinstance(d, dict):
      tmp = list(d.values())
    
    res = []
    for i in tmp:
      if i.isnumeric():
        res.append(i)
    return res

  except Exception as e:    
    capture_message(str(e), level="error")
    return []

def parse_str_list(d):
  try:
    if d and isinstance(d, str):
      tmp = [t.strip() for t in d.strip().split(',') if t.strip()]
      return tmp
    return []
  except Exception as e:
    capture_message(str(e), level="error")
    return []

def parse_bool(b):
  if not b:
    return False
  return ((isinstance(b, bool) and b) or (b == 'true') or (b == '1') or (b == 1) or (b == 'True'))

def parse_string(s):
  try:
    s = str(s)
    if s == 'undefined' or s == 'null':
      return None
    return s
  except Exception as e:
    capture_message(str(e), level="error")
    return None

def parse_int(b):
  try:
    return int(b)
  except Exception as e:
    capture_message(str(e), level="error")
    return 1

def parse_date(d):
  try:
    if len(d) == 10:
      return pytz.utc.localize(datetime.strptime(d, '%Y-%m-%d'))
    else:
      return pytz.utc.localize(datetime.strptime(d, '%Y-%m-%d %H:%M'))

  except Exception as e:
    capture_message(str(e), level="error")
    return timezone.now()

def rename_field(args, old_name, new_name):
  oldVal = args.pop(old_name, None)
  if oldVal:
    args[new_name] = oldVal
  return args

def rename_fields(args, pairs):
  for (old_name, new_name) in pairs:
    args = rename_field(args, old_name, new_name)
  return args


def serialize_all(data, full=False):
  if full:
    return [d.full_json() for d in data]
  return [d.simple_json() for d in data]


def serialize(data, full=False):
  if not data:
    return {}
  if full:
    return data.full_json()
  return data.simple_json()

def check_length(args, field,  min_length=5, max_length=40):
  data = args.get(field, None)
  if not data:
    return False, CustomMassenergizeError(f"Please provide a {field} field")
  
  data_length = len(data)
  if data_length < min_length or data_length > max_length:
    return False, CustomMassenergizeError(f"{field} has to be between {min_length} and {max_length}")
  return True, None

def parse_location(args):
  location = {
    "address": args.pop("address", None),
    "unit": args.pop("unit", None),
    "city": args.pop("city", None),
    "state": args.pop("state", None),
    "zipcode": args.pop("zipcode", None),
    "country": args.pop("country", 'US'),
  }
  args['location'] = location
  return args

def extract_location(args):
  location = {
    "address": args.pop("address", None),
    "unit": args.pop("unit", None),
    "city": args.pop("city", None),
    "state": args.pop("state", None),
    "zipcode": args.pop("zipcode", None),
    "country": args.pop("country", 'US'),
  }
  
  return location

def is_value(b):
  if b and b != 'undefined' and b != "NONE":
    return True
  return False

#def resize_image(img, options={}):
#  if options.get("is_logo", False):
#    size = options.get("size", 500)
#    width = options.get("width", 250)
#    height = options.get("height", 100)
#    dimension = (width, height)
#    new_img = cv2.resize(img, dsize=size, dim=dimension, interpolation = cv2.INTER_AREA)
#    return new_img
#  else:
#    size = options.get("size", 500)
#    new_img = cv2.resize(img, dsize=size, interpolation = cv2.INTER_AREA)
#    return new_img

def _common_name(s):
  return (' '.join(s.split('_'))).title()

def validate_fields(args, checklist):
  for field in checklist:
    if field not in args:
      return False, CustomMassenergizeError(f"You are missing: {_common_name(field)}")
  return True, None

def get_cookie(request, key):
  cookie = request.COOKIES.get(key)
  if cookie and len(cookie) > 0:
      return cookie
  else:
      return None 

def set_cookie(response, key, value): # TODO
  print(f"----- set_cookie: {response}")
  # set cookie on response before sending
  # cookie expiration set to 1yr
  MAX_AGE = 31536000

  response.set_cookie(key, value, MAX_AGE, samesite='Strict')
