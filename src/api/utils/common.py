import json 
import querystring
from querystring_parser import parser


def get_request_contents(request):
  try:
    if request.method != 'POST' :
      return request.GET.dict()

    args = {}
    if request.content_type == 'application/x-www-form-urlencoded':
      tmp = parser.parse(request.POST.urlencode())
      args= tmp
      
      # print(tmp)
      # for k, v in tmp.items():
      #   if(isinstance(v, dict)):
      #     args[k] = list(v.values())
      #   elif isinstance(v, str) and v.isnumeric():
      #     args = int(v)
      #   else:
      #     args[k] = v
    elif request.content_type == 'multipart/form-data':
      tmp = request.POST.dict()
      if(request.FILES):
        for i in request.FILES.dict():
          args[i] = request.FILES[i]
    else:
      args = request.POST.dict()
    return args

  except Exception as e:
    print(e)
    return {}


def parse_list(d):
  try:
    if isinstance(d, str):
      return d.split(',')
    elif isinstance(d, dict):
      return list(d.values())
    else:
      return []
  except Exception as e:
    print(e)
    return []

def parse_bool(b):
  return (b == 'true') or (b == '1') or (b == 1) or (b == 'True')

def serialize_all(data, full=False):
  if full:
    return [d.full_json() for d in data]
  return [d.simple_json() for d in data]


def serialize(data, full=False):
  if full:
    return data.full_json()
  return data.simple_json()