from django.shortcuts import render
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.settings import DEPLOY_VERSION, RELEASE_NOTES

# Create your views here.
def home(request):
  return render(request, 'index.html', {'build_version': DEPLOY_VERSION, 'release_notes': RELEASE_NOTES})

def handler400(request, exception):
  #TODO: do some logging here
  return MassenergizeResponse(error="Error: BadRequest")

def handler403(request, exception):
  return MassenergizeResponse(error="Error: PermissionDenied")

def handler404(request, exception):
  return MassenergizeResponse(data=f"path: {request.build_absolute_uri()}", error="Error: ResourceNotFound")

def handler500(request):
  return MassenergizeResponse(error="Error: ServerError")