LIST = [
  'community/<int:cid>/actions',
  'community/<int:cid>/members',
  'community/<int:cid>/impact',
  'community/<int:cid>/pages',
  'community/<int:cid>/events',
  'community/<int:cid>/households',
  'community/<int:cid>/goals',
  'community/<int:cid>/teams',
  'community/<int:cid>/data',
  'community/<int:cid>/testimonials',
  'community/<int:cid>/stories',
]

def clean(s):
	if ':' in s:
		s = s[1:-1] #trim < and > from beginning and end
		s = s.split(':')[-1]
	return s.replace('-', '_')

def get_params(lst):
	return ', '.join( [clean(p) for p in lst if '<' in p] )

def get_func_name(lst):
	return '_'.join( [clean(p) for p in lst if '<' not in p] )

def get_model_name(s):
	s = s.replace("-"," ").title().replace(" ", "").replace("ies", "y")
	if s[-1] == 's':
		return s[:-1]
	return s


def generate_views(lst):
	for r in lst:
		parts = r.split('/')
		if(len(parts) == 1):
			#it is the plural generic one
			func_name = clean(parts[0])
			# print(f"path('{r}', {func_name}),")

			model_name = get_model_name(parts[0])
			result = f"\n\
			@csrf_exempt\n\
			def {func_name}(request):\n\
				args = get_request_contents(request)\n\
				if request.method == 'GET':\n\
					{model_name.lower()}s, errors = FETCH.all({model_name}, args)\n\
					return Json({model_name}s, errors)\n\
				elif request.method == 'POST':\n\
					#about to create a new {model_name} instance\n\
					{model_name.lower()}, errors = FACTORY.create({model_name}, args)\n\
					return Json({model_name.lower()}, errors)\n\
				return Json(None)\n\n"
			print(result)
		else:
			params = ', ' + get_params(parts[1:])
			func_name = get_func_name(parts)
			model_name = get_model_name(parts[0])
			# print(f"path('{r}', {func_name}),")
			result = f"\n\
			@csrf_exempt\n\
			def {func_name}(request{params}):\n\
				args = get_request_contents(request)\n\
				args['id'] = id\n\
				if request.method == 'GET':\n\
					{model_name.lower()}, errors = FETCH.one({model_name}, args)\n\
					return Json({model_name.lower()}, errors)\n\
				elif request.method == 'POST':\n\
					#updating the {model_name} resource with this <id>\n\
					{model_name.lower()}, errors = FACTORY.create({model_name}, args)\n\
					return Json({model_name.lower()}, errors)\n\
				return Json(None)\n\n"		
			print(result)

generate_views(LIST)