import html2text
import traceback
from django.shortcuts import render, redirect
from _main_.utils.massenergize_response import MassenergizeResponse
from django.http import Http404
from _main_.settings import IS_PROD, IS_CANARY, RUN_SERVER_LOCALLY
from sentry_sdk import capture_message
from api.store.misc import MiscellaneousStore
from _main_.utils.constants import RESERVED_SUBDOMAIN_LIST, STATES
from database.models import (
    Deployment,
    Community,
    Event,
    Team,
    Vendor,
    Action,
    Testimonial,
    AboutUsPageSettings,
    ContactUsPageSettings,
    DonatePageSettings,
    ImpactPageSettings,
    CustomCommunityWebsiteDomain,
)

extract_text_from_html = html2text.HTML2Text()
extract_text_from_html.ignore_links = True

HOME_SUBDOMAIN_SET = set([
    "communities",
    "communities-dev",
    "communities-canary",
    "search",
    "search-dev",
    "search-canary",
    "share",
    "share-dev",
    "share-canary",
])

IS_LOCAL = RUN_SERVER_LOCALLY       # API and community portal running locally
if IS_LOCAL:
    PORTAL_HOST = "http://massenergize.test:3000"
elif IS_CANARY:
    PORTAL_HOST = "https://community-canary.massenergize.org"
elif IS_PROD:
    PORTAL_HOST = "https://community.massenergize.org"


else:
    # we know it is dev
    PORTAL_HOST = "https://community.massenergize.dev"


if IS_LOCAL:
    HOST_DOMAIN = "http://communities.massenergize.test:8000"
    HOST = f"{HOST_DOMAIN}"
elif IS_PROD:
    # TODO treat canary as a separate thing
    HOST_DOMAIN = "massenergize.org"
    HOST = f"https://communities.{HOST_DOMAIN}"
elif IS_CANARY:
    HOST_DOMAIN = "massenergize.org"
    HOST = f"https://communities-canary.{HOST_DOMAIN}"
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


def _get_is_sandbox(request):
    query = request.META["QUERY_STRING"]
    if len(query) > 1:
        pars = query.split(",")
        for par in pars:
            ps = par.split("=")
            if ps[0].lower() == "sandbox":
                if len(ps) < 2 or ps[1].lower() == "true":
                    print("it is the sandbox")
                    return True
                return False    # sandbox=false
        return False            # sandbox not specified
    return False                # no query string


def _get_redirect_url(subdomain, community=None, is_sandbox=False):

    if not community and subdomain:
        if is_sandbox:
            community = Community.objects.filter(
                is_deleted=False,
                subdomain__iexact=subdomain,
            ).first()
        else:
            community = Community.objects.filter(
                is_deleted=False,
                is_published=True,
                subdomain__iexact=subdomain,
            ).first()

    if not community:
        raise Http404

    suffix = ""
    if is_sandbox:
        suffix = "?sandbox=true"
    redirect_url = f"{PORTAL_HOST}/{subdomain}{suffix}"
    community_website_search = CustomCommunityWebsiteDomain.objects.filter(
        community=community).first()
    if community_website_search:
        redirect_url = f"https://{community_website_search.website}"
    return redirect_url


def _get_file_url(image):
    if not image:
        return None
    return image.file.url if image.file else None


def home(request):
    subdomain = _get_subdomain(request, False)
    if not subdomain or subdomain in HOME_SUBDOMAIN_SET:
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

    is_sandbox = _get_is_sandbox(request)
    if is_sandbox:
        communityList = list(Community.objects.filter(
            is_deleted=False
        ).values("id", "name", "subdomain", "about_community", "location"))
        suffix = "?sandbox=true"
    else:
        communityList = list(Community.objects.filter(
            is_deleted=False, is_published=True
        ).values("id", "name", "subdomain", "about_community", "location"))
        suffix = ""

    # for each community make a display name which is "Location - Community name"
    for community in communityList:
        location = community.get("location", None)
        prefix = ""
        if location:
            city = location["city"]
            state = location["state"]
            if state:
                for abbrev, name in STATES.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
                    if state.lower() == name.lower():
                        prefix = abbrev + ' - '
            if city:
                prefix = city + ", " + prefix
        displayName = prefix + community["name"]
        index = communityList.index(community)
        communityList[index]["displayName"] = displayName

    # sort the list by the display name
    def sortFunc(e):
        return e['displayName']
    communityList.sort(key=sortFunc)

    args = {
        "meta": meta,
        "communities": communityList,
        "sandbox": is_sandbox,
        "suffix": suffix,
    }
    return render(request, "communities.html", args)


def community(request, subdomain):
    if not subdomain:
        return communities(request)

    is_sandbox = _get_is_sandbox(request)
    if is_sandbox:
        community = Community.objects.filter(
            is_deleted=False,
            subdomain__iexact=subdomain,
        ).first()
    else:
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

    redirect_url = _get_redirect_url(subdomain, community, is_sandbox)

    meta = META
    meta.update(
        {
            "image_url": _get_file_url(community.logo),
            "subdomain": subdomain,
            "section": f"#community#{subdomain}",
            "redirect_to": redirect_url,
            "title": str(community),
            "description": _extract(about.description),
            "url": redirect_url,
            "created_at": community.created_at,
            "updated_at": community.updated_at,
            "tags": ["#ClimateChange", community.subdomain],
            "stay_put": request.GET.get('stay_put', None),
        }
    )

    args = {"meta": meta, "community": community, "about": about}
    return render(request, "community.html", args)


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

    return render(request, "actions.html", args)


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
            "image_url": _get_file_url(action.image),
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
    return render(request, "action.html", args)


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
    return render(request, "events.html", args)


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
            "image_url": _get_file_url(event.image),
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
    return render(request, "event.html", args)


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
    return render(request, "services.html", args)


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
            "image_url": _get_file_url(vendor.logo),
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

    return render(request, "service.html", args)


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
    return render(request, "teams.html", args)


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
    return render(request, "team.html", args)


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
    return render(request, "testimonials.html", args)


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
    return render(request, "testimonial.html", args)


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

    return render(request, "page__about_us.html", args)


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

    return render(request, "page__donate.html", args)


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

    return render(request, "page__impact.html", args)


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

    return render(request, "page__contact_us.html", args)


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
