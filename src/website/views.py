from django.shortcuts import render
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Deployment
from _main_.settings import IS_PROD
from sentry_sdk import capture_message

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
  error_msg = "bad_request"
  # capture_message("Bad Request", level="error")
  return MassenergizeResponse(error=error_msg)

def handler403(request, exception):
  error_msg = "permission_denied"
  capture_message(error_msg, level="error")
  return MassenergizeResponse(error=error_msg)

def handler404(request, exception):
  error_msg = "page_not_found"
  capture_message(error_msg, level="error")
  return MassenergizeResponse(data=f"path: {request.build_absolute_uri()}", error=error_msg)

def handler500(request):
  error_msg = "server_error"
  capture_message(error_msg, level="error")
  return MassenergizeResponse(error=error_msg)
