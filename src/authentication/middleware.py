"""
Middle ware for authorization for users before they access specific resources
"""
from _main_.settings import FIREBASE_CREDENTIALS
import json


class MassenergizeJWTAuthMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response
    self.unrestricted_paths = set([

    ])

    # One-time configuration and initialization.

  def __call__(self, request):
    # Code to be executed for each request before
    # the view (and later middleware) are called.

    response = self.get_response(request)

    # Code to be executed for each request/response after
    # the view is called.

    return response
  

  def _get_auth_token(self, request):
    authz = request.headers.get('Authorization', None)
    if not authz:
      return 
    id_token = authz.split(' ')
    print(id_token)



  def process_view(self, request, view_func, *view_args, **view_kwargs):
    #extract JWT auth token
    #print(request.headers)
    id_token = self._get_auth_token(request)
    pass
    # try:
    #   payload = json.loads(request.body.decode('utf-8'))
    #   id_token = payload.get('idToken', None)
    #   if id_token:
    #     decoded_token = auth.verify_id_token(id_token)
    #     uid = decoded_token['uid']
    #     return Json({"login": "successful", "user": uid, "decoded_token": decoded_token})
    #   else:
    #     return Json(errors=['Invalid Auth'])
    # except Exception as e:
    #   return Json(errors=[str(e)])
