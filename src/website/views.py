from django.shortcuts import render
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Deployment
from _main_.settings import IS_PROD, IS_CANARY, BASE_DIR
from sentry_sdk import capture_message
from _main_.utils.utils import load_json, load_text_contents
from api.store.misc import MiscellaneousStore

# Create your views here.
def home(request):
  print('hello search')
  return MassenergizeResponse(data=True)


def generate_sitemap(request):
  d = MiscellaneousStore().generate_sitemap_for_portal()
  return render(request, 'sitemap_template.xml', d, content_type='text/xml')


def handler400(request, exception):
  return MassenergizeResponse(error="bad_request")

def handler403(request, exception):
  return MassenergizeResponse(error="permission_denied")

def handler404(request, exception):
  if request.path.startswith("/v2"):
    return MassenergizeResponse(error="method_deprecated")
  return MassenergizeResponse(error="resource_not_found")

def handler500(request):
  import traceback
  capture_message(str(traceback.print_exc()))
  return MassenergizeResponse(error="server_error")
