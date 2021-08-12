from django.shortcuts import render
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Deployment, Community
from _main_.settings import IS_PROD, IS_CANARY, BASE_DIR
from sentry_sdk import capture_message
from _main_.utils.utils import load_json, load_text_contents
from api.store.misc import MiscellaneousStore
from api.services.misc import MiscellaneousService

HOST = 'apomden.test:8000'

RESERVED_LIST = set([
  '', '*', 'massenergize', 'api', 'admin', 'admin-dev', 'admin-canary', 'administrator', 'auth', 'authentication'
])

def _get_subdomain(request):
  domain_components = request.META['HTTP_HOST'].split('.')
  if len(domain_components) <= 2:
    return "" # we don't really have a subdomain in this case.
  return domain_components[0]

def _subdomain_is_valid(subdomain):
  if subdomain in RESERVED_LIST:
    return False

  # TODO: switch to using the subdomain model to check this
  return Community.objects.filter(subdomain__iexact=subdomain).exists()


# Create your views here.
def home(request):
  subdomain = _get_subdomain(request)
  if _subdomain_is_valid(subdomain):
    return community(request, subdomain)

  # TODO: redirect here instead of just serving the request
  return communities(request)


def communities(request):
  args = {
    'host': HOST,
    'communities': Community.objects.filter(
      is_deleted=False, 
      is_published=True
    ).values('id', 'name',  'subdomain', 'about_community'),
  }
  return render(request, 'communities.html', args  )

def community(request, subdomain):
  args = {
    'host': HOST,
    'communities': Community.objects.filter(
      is_deleted=False, 
      is_published=True,
      subdomain=subdomain,
    ).values('id', 'name',  'subdomain', 'about_community'),
  }
  return render(request, 'community.html', args)

def actions(request):
  return render(request, 'actions.html', {})

def action(request, id):
  return render(request, 'action.html', {})

def events(request):
  return render(request, 'events.html', {})

def event(request, id):
  return render(request, 'event.html', {})

def vendors(request):
  return render(request, 'services.html', {})

def vendor(request, id):
  return render(request, 'service.html', {})

def teams(request):
  return render(request, 'teams.html', {})

def team(request, id):
  return render(request, 'team.html', {})

def testimonials(request):
  return render(request, 'testimonials.html', {})

def testimonial(request, id):
  return render(request, 'testimonial.html', {})


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
