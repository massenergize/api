from django.shortcuts import render
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Deployment
from _main_.settings import IS_PROD

# Create your views here.
def home(request):
  deployments = Deployment.objects.all()[:3]

  if IS_PROD:
    SITE_TITLE = 'MassEnergize-API'
    SITE_BACKGROUND_COLOR = '#310161'
    SITE_FONT_COLOR = 'white'
  else:
    SITE_TITLE = 'DEV: MassEnergize-API'
    SITE_BACKGROUND_COLOR = '#0b5466'
    SITE_FONT_COLOR = 'white'

  return render(request, 'index.html', {
      'deployments': deployments,
      'SITE_TITLE': SITE_TITLE,
      'SITE_BACKGROUND_COLOR': SITE_BACKGROUND_COLOR,
      'SITE_FONT_COLOR': SITE_FONT_COLOR
    }
  )

def handler400(request, exception):
  #TODO: do some logging here
  return MassenergizeResponse(error="Error: BadRequest")

def handler403(request, exception):
  return MassenergizeResponse(error="Error: PermissionDenied")

def handler404(request, exception):
  return MassenergizeResponse(data=f"path: {request.build_absolute_uri()}", error="Error: ResourceNotFound")

def handler500(request):
  return MassenergizeResponse(error="Error: ServerError")