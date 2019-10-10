from django.shortcuts import render
from api.utils.massenergize_response import MassenergizeResponse


# Create your views here.
def home(request):
  return render(request, 'index.html')

def handler400(request):
  return MassenergizeResponse(data=None, error="Error: BadRequest")

def handler403(request):
  return MassenergizeResponse(data=None, error="Error: ResourceNotFound")

def handler404(request):
  return MassenergizeResponse(data=None, error="Error: PermissionDenied")

def handler500(request):
  return MassenergizeResponse(data=None, error="Error: ServerError")