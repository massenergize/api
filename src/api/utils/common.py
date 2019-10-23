import json 
from querystring_parser import parser
from api.api_errors.massenergize_errors import CustomMassenergizeError
import pytz
from django.utils import timezone
from datetime import datetime

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
    args = rename_field(args, 'is_dev', 'is_published')
    return args

  except Exception as e:
    return {}

def parse_list(d):
  try:
    if isinstance(d, str):
      return d.strip().split(',') if d else []
    elif isinstance(d, dict):
      return list(d.values())
    else:
      return []
  except Exception as e:
    print(e)
    return []

def parse_bool(b):
  if not b:
    return False
  return ((isinstance(b, bool) and b) or (b == 'true') or (b == '1') or (b == 1) or (b == 'True'))

def parse_int(b):
  try:
    return int(b)
  except Exception as e:
    print(e)
    return 1

def parse_date(d):
  try:
    return pytz.utc.localize(datetime.strptime(d, '%Y-%m-%d %H:%M'))
  except Exception as e:
    print(e)
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
  if full:
    return data.full_json()
  return data.simple_json()

def check_length(args, field,  min_length=5, max_length=25):
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
    "country": args.pop("country", None),
  }
  args['location'] = location
  return args