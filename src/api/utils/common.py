import json 


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
      return {}

