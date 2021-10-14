import html2text, traceback
from django.shortcuts import render, redirect
from _main_.utils.massenergize_response import MassenergizeResponse
from django.http import Http404
from _main_.settings import IS_PROD, IS_CANARY, BASE_DIR, IS_LOCAL
from sentry_sdk import capture_message
from _main_.utils.utils import load_json, load_text_contents
from api.store.deviceprofile import DeviceStore
from api.store.misc import MiscellaneousStore
from api.services.misc import MiscellaneousService
from _main_.utils.constants import RESERVED_SUBDOMAIN_LIST
from database.models import (
    Deployment,
    Community,
    Event,
    Team,
    Vendor,
    Action,
    Testimonial,
    DeviceProfile,
    AboutUsPageSettings,
    ContactUsPageSettings,
    DonatePageSettings,
    ImpactPageSettings,
    CustomCommunityWebsiteDomain,
)

extract_text_from_html = html2text.HTML2Text()
extract_text_from_html.ignore_links = True

HOME_SUBDOMAIN_SET = set(["communities", "search", "community"])

if IS_LOCAL:
    #TODO: update this with localhost if you are running the frontend locally
    # PORTAL_HOST = "https://community.massenergize.dev"
    PORTAL_HOST = "http://localhost:3000"
elif IS_CANARY:
    PORTAL_HOST = "https://community-canary.massenergize.org"
elif IS_PROD:
    PORTAL_HOST = "https://community.massenergize.org"
else:
    # we know it is dev 
    PORTAL_HOST = "https://community.massenergize.dev"


if IS_LOCAL:
    # HOST_DOMAIN = "massenergize.dev"
    # HOST = f"http://{HOST_DOMAIN}"
    HOST_DOMAIN = "localhost:8000"
    HOST = f"http://communities.{HOST_DOMAIN}"
    
    
elif IS_PROD or IS_CANARY:
    #TODO treat canary as a separate thing
    HOST_DOMAIN = "massenergize.org"
    HOST = f"https://communities.{HOST_DOMAIN}"
else:
    HOST_DOMAIN = "massenergize.dev"
    HOST = f"https://communities.{HOST_DOMAIN}"


META = {
    "site_name": "Massenergize",
    "host": HOST,
    "host_domain": HOST_DOMAIN,
    "title": "Massenergize Communities",
    "portal_host": PORTAL_HOST,
    "section": f"#community",
    "tags": ["#ClimateChange"],
    "is_local": IS_LOCAL
}


def _get_subdomain(request, enforce_is_valid=False):
    domain_components = request.META["HTTP_HOST"].split(".")
    if len(domain_components) <= 2:
        if not enforce_is_valid:
            return ""  # we don't really have a subdomain in this case.
        else:
            raise Http404

    subdomain = domain_components[0]
    if enforce_is_valid:
        if not _subdomain_is_valid(subdomain):
            raise Http404

    return subdomain


def _subdomain_is_valid(subdomain):
    if subdomain in RESERVED_SUBDOMAIN_LIST:
        return False

    # TODO: switch to using the subdomain model to check this
    return Community.objects.filter(subdomain__iexact=subdomain).exists()

def _extract(html):
    res = extract_text_from_html.handle(html) 
    return f"{res.strip()[:250]}..."

def _get_redirect_url(subdomain, community=None):

    if not community:
        community = Community.objects.filter(
            is_deleted=False,
            is_published=True,
            subdomain__iexact=subdomain,
        ).first()

    if not community:
        raise Http404

    redirect_url = f"{subdomain}.{HOST_DOMAIN}"
    community_website_search = CustomCommunityWebsiteDomain.objects.filter(community=community).first()
    if community_website_search:
        redirect_url = f"https://{community_website_search.website}" 
    return redirect_url

def _get_file_url(image):
    if not image:
        return None
    return image.file.url if image.file else None

def _get_cookie(request, key):
    cookie = request.COOKIES.get(key)
    if cookie and len(cookie) > 0:
        return cookie
    else:
        return None 

def _set_cookie(response, key, value): # TODO 
    # set cookie on response before sending
    # cookie expiration set to 1yr
    MAX_AGE = 31536000

    response.set_cookie(key, value, MAX_AGE, samesite='Strict')

def _get_device(device_id): # TODO 
    pass

def _log_device(device_id): # TODO 
    pass

def _log_user(device_id): # TODO 
    pass

def _log_device(request, response):

    # Cookies
    # get cookie
    cookie = _get_cookie(request, "device")

    # have we seen this device before?
    if cookie: # yes
        print("----- Device in cookie found")
        try:
            device = DeviceProfile.objects.filter(id=cookie).first()
        except Exception as e:
            pass # TODO do something if device is not in database
         # TODO update device log
    else: # no
        print("----- Device in cookie not found")
        device_info = {
            "ip_address": "0.0.0.0", # TODO get IP address
            "device_type": "macbook", # TODO get device type
            "operating_system": "MacOS", # TODO get operating system
            "browser": "Chrome", # TODO get browser
        }
        device: DeviceProfile = DeviceProfile.objects.create() # TODO create device profile
        print("----- Device created")
        if device_info["ip_address"]:
            device.ip_address = device_info["ip_address"]
            print("---------- Device ip")
        if device_info["device_type"]:
            device.device_type = device_info["device_type"]
            print("---------- Device type")
        if device_info["operating_system"]:
            device.operating_system = device_info["operating_system"]
            print("---------- Device OS")
        if device_info["browser"]:
            device.browser = device_info["browser"]
            print("---------- Device browser")
        device.save()

    _set_cookie(response, "device", device.id) # TODO save cookie

def home(request):
    subdomain = _get_subdomain(request, False)
    if not subdomain or subdomain in HOME_SUBDOMAIN_SET :
        return communities(request)
    elif _subdomain_is_valid(subdomain):
        return community(request, subdomain)

    return redirect(HOST)


def communities(request):
    meta = META
    meta.update(
        {
            "title": "Massenergize Communities",
            "redirect_to": f"{PORTAL_HOST}",
            "stay_put": True,
        }
    )
    args = {
        "meta": META,
        "communities": Community.objects.filter(
            is_deleted=False, is_published=True
        ).values("id", "name", "subdomain", "about_community"),
    }

    response = render(request, "communities.html", args)

    _log_device(request, response)
    
    return response


def community(request, subdomain):
    if not subdomain:
        return communities(request)

    community = Community.objects.filter(
        is_deleted=False,
        is_published=True,
        subdomain__iexact=subdomain,
    ).first()

    if not community:
        raise Http404

    about = (
        AboutUsPageSettings.objects.filter(
            is_deleted=False, community__subdomain__iexact=subdomain
        ).first()
        or {}
    )

    redirect_url = _get_redirect_url(subdomain, community)
    
    meta = META
    meta.update(
        {
            "image_url": _get_file_url(community.logo),    
            "subdomain": subdomain,
            "section": f"#community#{subdomain}",
            "redirect_to": redirect_url,
            "title": str(community),
            "description": _extract(about.description),
            "url": f"{PORTAL_HOST}/{subdomain}",
            "created_at": community.created_at,
            "updated_at": community.updated_at,
            "tags": ["#ClimateChange", community.subdomain],
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {"meta": meta, "community": community, "about": about}

    response = render(request, "community.html", args)
    
    _set_cookie(response, "device", "Community1")

    # _log_device(request, response)

    return response


def actions(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
        
    redirect_url = _get_redirect_url(subdomain, None)

    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Take Action",
            "redirect_to": f"{redirect_url}/actions",
            "stay_put": request.GET.get('stay_put', None),
        }
    )
    args = {
        "meta": meta,
        "actions": Action.objects.filter(
            is_deleted=False, is_published=True, community__subdomain__iexact=subdomain
        ).values("id", "title", "featured_summary"),
    }

    response = render(request, "actions.html", args)

    _set_cookie(response, "Actions", "Actions1")

    return response


def action(request, id, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)

    action = Action.objects.filter(
        pk=id,
        community__subdomain__iexact=subdomain,
        is_deleted=False,
        is_published=True,
    ).first()

    if not action:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "image_url":_get_file_url(action.image),
            "subdomain": subdomain,
            "title": action.title,
            "description": _extract(action.about),
            "url": f"{redirect_url}/actions/{id}",
            "redirect_to": f"{redirect_url}/actions/{id}",
            "created_at": action.created_at,
            "updated_at": action.updated_at,
            "stay_put": request.GET.get('stay_put', None),
        }
    )
    args = {"meta": meta, "action": action}
    
    response = render(request, "action.html", args)

    _set_cookie(response, "Action", "Action1")

    return response


def events(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Attend an event near you",
            "redirect_to": f"{redirect_url}/events",
            "stay_put": request.GET.get('stay_put', None),
        }
    )
    args = {
        "meta": meta,
        "events": Event.objects.filter(
            is_deleted=False, is_published=True, community__subdomain__iexact=subdomain
        ).values(
            "id", "name", "start_date_and_time", "end_date_and_time", "featured_summary"
        ),
    }

    response = render(request, "events.html", args)

    _set_cookie(response, "Events", "Events1")

    return response


def event(request, id, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    event = Event.objects.filter(
        is_deleted=False,
        is_published=True,
        pk=id,
        community__subdomain__iexact=subdomain,
    ).first()

    if not event:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": event.name,
            "image_url":_get_file_url(event.image),
            "subdomain": subdomain,
            "description": _extract(event.description),
            "redirect_to": f"{redirect_url}/events/{id}",
            "url": f"{redirect_url}/events/{id}",
            "stay_put": request.GET.get('stay_put', None),
        }
    )
    args = {
        "meta": meta,
        "event": event,
    }

    response = render(request, "event.html", args)

    _set_cookie(response, "Event", "Event1")

    return response


def vendors(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    community = Community.objects.filter(
        subdomain__iexact=subdomain, is_deleted=False, is_published=True
    ).first()
    if not community:
        raise Http404
    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Services & Vendors",
            "redirect_to": f"{redirect_url}/services",
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "vendors": community.community_vendors.filter(is_deleted=False).values(
            "id", "name", "description", "service_area"
        ),
    }
    response = render(request, "services.html", args)

    _set_cookie(response, "Vendors", "Vendors1")

    return response


def vendor(request, id, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    vendor = Vendor.objects.filter(is_deleted=False, pk=id).first()

    if not vendor:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": vendor.name,
            "image_url":_get_file_url(vendor.logo),
            "subdomain": subdomain,
            "description": _extract(vendor.description),
            "redirect_to": f"{redirect_url}/services/{id}",
            "url": f"{redirect_url}/services/{id}",
            "created_at": vendor.created_at,
            "updated_at": vendor.updated_at,
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "vendor": vendor,
    }

    response = render(request, "service.html", args)

    _set_cookie(response, "Vendor", "Vendor1")

    return response


def teams(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    community = Community.objects.filter(
        subdomain__iexact=subdomain, is_deleted=False, is_published=True
    ).first()

    teams = community.community_teams.filter(
        is_deleted=False, is_published=True
    ).values("id", "name", "tagline") | community.primary_community_teams.filter(
        is_deleted=False, is_published=True
    ).values(
        "id", "name", "tagline"
    )
    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Teams",
            "redirect_to": f"{redirect_url}/teams",
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "teams": teams,
    }

    response = render(request, "teams.html", args)

    _set_cookie(response, "Teams", "Teams1")

    return response


def team(request, id, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    team = Team.objects.filter(
        is_deleted=False,
        is_published=True,
        pk=id,
    ).first()

    # TODO: check that this team is listed under this community

    if not team:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": team.name,
            "image_url": _get_file_url(team.logo),
            "subdomain": subdomain,
            "description": _extract(team.description),
            "redirect_to": f"{redirect_url}/teams/{id}",
            "url": f"{redirect_url}/teams/{id}",
            "created_at": team.created_at,
            "updated_at": team.updated_at,
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "team": team,
    }

    response = render(request, "team.html", args)

    _set_cookie(response, "Team", "Team1")

    return response


def testimonials(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Teams",
            "redirect_to": f"{redirect_url}/testimonials",
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "title": "Testimonials and User Stories",
        "testimonials": Testimonial.objects.filter(
            is_deleted=False, is_published=True, community__subdomain__iexact=subdomain
        ).values("id", "title", "body"),
    }

    response = render(request, "testimonials.html", args)

    _set_cookie(response, "Testimonials", "Testimonials1")

    return response


def testimonial(request, id, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    testimonial = Testimonial.objects.filter(
        is_deleted=False,
        is_published=True,
        pk=id,
        community__subdomain__iexact=subdomain,
    ).first()

    if not testimonial:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(testimonial),
            "image_url": _get_file_url(testimonial.image),
            "subdomain": subdomain,
            "description": _extract(testimonial.body),
            "redirect_to": f"{redirect_url}/testimonials/{id}",
            "url": f"{redirect_url}/testimonials/{id}",
            "created_at": testimonial.created_at,
            "updated_at": testimonial.updated_at,
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "testimonial": testimonial,
    }

    response = render(request, "testimonial.html", args)

    _set_cookie(response, "Testimonial", "Testimonial1")

    return response


def about_us(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    page = AboutUsPageSettings.objects.filter(
        is_deleted=False, community__subdomain__iexact=subdomain
    ).first()

    if not page:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(page),
            "redirect_to": f"{redirect_url}/aboutus",
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "page": page,
    }

    response = render(request, "page__about_us.html", args)

    _set_cookie(response, "About", "About1")

    return response


def donate(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    page = DonatePageSettings.objects.filter(
        is_deleted=False, community__subdomain__iexact=subdomain
    ).first()

    if not page:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(page),
            "redirect_to": f"{redirect_url}/donate",
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "page": page,
    }

    response = render(request, "page__donate.html", args)

    _set_cookie(response, "Donate", "Donate1")

    return response


def impact(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    page = ImpactPageSettings.objects.filter(
        is_deleted=False, community__subdomain__iexact=subdomain
    ).first()

    if not page:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(page),
            "redirect_to": f"{redirect_url}/impact",
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "page": page,
    }

    response = render(request, "page__impact.html", args)

    _set_cookie(response, "Impact", "Impact1")

    return response


def contact_us(request, subdomain=None):
    if not subdomain:
        subdomain = _get_subdomain(request, enforce_is_valid=True)
    page = ContactUsPageSettings.objects.filter(
        is_deleted=False, community__subdomain__iexact=subdomain
    ).first()

    if not page:
        raise Http404

    redirect_url = _get_redirect_url(subdomain, None)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(page),
            "redirect_to": f"{redirect_url}/impact",
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {
        "meta": meta,
        "page": page,
    }

    response = render(request, "page__contact_us.html", args)

    _set_cookie(response, "Contact", "Contact1")

    return response


def generate_sitemap(request):
    d = MiscellaneousStore().generate_sitemap_for_portal()
    return render(request, "sitemap_template.xml", d, content_type="text/xml")

def generate_sitemap_main(request):
    d = MiscellaneousStore().generate_sitemap_for_portal()
    return render(request, "sitemap_template_new.xml", d, content_type="text/xml")


def handler400(request, exception):
    return MassenergizeResponse(error="bad_request")


def handler403(request, exception):
    return MassenergizeResponse(error="permission_denied")


def handler404(request, exception):
    if request.path.startswith("/v2"):
        return MassenergizeResponse(error="method_deprecated")
    return MassenergizeResponse(error="resource_not_found")


def handler500(request):
    capture_message(str(traceback.print_exc()))
    return MassenergizeResponse(error="server_error")
