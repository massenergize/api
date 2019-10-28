from django.shortcuts import render
from _main_.utils.massenergize_response import MassenergizeResponse


# Create your views here.
def home(request):
  return render(request, 'index.html')

def handler400(request, exception):
  #TODO: do some logging here
  return MassenergizeResponse(error="Error: BadRequest")

def handler403(request, exception):
  return MassenergizeResponse(error="Error: PermissionDenied")

def handler404(request, exception):
  return MassenergizeResponse(data=f"path: {request.build_absolute_uri()}", error="Error: ResourceNotFound")

def handler500(request):
  return MassenergizeResponse(error="Error: ServerError")