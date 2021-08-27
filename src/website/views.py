from django.shortcuts import render, redirect
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import (
    Deployment,
    Community,
    Event,
    Team,
    Vendor,
    Action,
    Testimonial,
)
from _main_.settings import IS_PROD, IS_CANARY, BASE_DIR
from sentry_sdk import capture_message
from _main_.utils.utils import load_json, load_text_contents
from api.store.misc import MiscellaneousStore
from api.services.misc import MiscellaneousService
import html2text
from django.http import Http404


extract_text_from_html = html2text.HTML2Text()
extract_text_from_html.ignore_links = True

HOST_DOMAIN = "massenergize.test:8000"
HOST = f"http://{HOST_DOMAIN}"
PORTAL_HOST = "https://community.massenergize.org"

RESERVED_LIST = set(
    [
        "",
        "*",
        "massenergize",
        "api",
        "admin",
        "admin-dev",
        "admin-canary",
        "administrator",
        "auth",
        "authentication",
        "community",
        "communities",
    ]
)

META = {
    "site_name": "Massenergize",
    "host": HOST,
    "host_domain": HOST_DOMAIN,
    "title": "Massenergize Communities",
    "portal_host": PORTAL_HOST,
    "section": f"#community",
    "tags": ["#ClimateChange"],
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
    if subdomain in RESERVED_LIST:
        return False

    # TODO: switch to using the subdomain model to check this
    return Community.objects.filter(subdomain__iexact=subdomain).exists()


# Create your views here.
def home(request):
    subdomain = _get_subdomain(request, False)
    print(subdomain)
    if not subdomain:
        return communities(request)
    elif _subdomain_is_valid(subdomain):
        return community(request, subdomain)

    return redirect(HOST)


def communities(request):
    meta = META
    meta.update(
        {
            "title": "Massenergize Communities",
        }
    )
    args = {
        "meta": META,
        "communities": Community.objects.filter(
            is_deleted=False, is_published=True
        ).values("id", "name", "subdomain", "about_community"),
    }
    return render(request, "communities.html", args)


def community(request, subdomain):
    community = Community.objects.filter(
        is_deleted=False,
        is_published=True,
        subdomain=subdomain,
    ).first()

    if not community:
        raise Http404

    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "section": f"#community#{subdomain}",
            "title": str(community),
            "description": extract_text_from_html.handle(community.about_community),
            "image": community.logo.file if community.logo else {},
            "url": f"{PORTAL_HOST}/{subdomain}",
            "created_at": community.created_at,
            "updated_at": community.updated_at,
            "tags": ["#ClimateChange", community.subdomain],
        }
    )

    args = {
        "meta": meta,
        "community": community,
    }
    return render(request, "community.html", args)


def actions(request):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Take Action",
        }
    )
    args = {
        "meta": meta,
        "actions": Action.objects.filter(
            is_deleted=False, is_published=True, community__subdomain=subdomain
        ).values("id", "title", "featured_summary"),
    }

    return render(request, "actions.html", args)


def action(request, id):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Take Action",
        }
    )
    args = {
        "meta": meta,
        "action": Action.objects.filter(
            pk=id,
            community__subdomain=subdomain,
            is_deleted=False,
            is_published=True,
        ).first(),  # TODO: handle None case
    }
    return render(request, "action.html", args)


def events(request):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Attend an event near you",
        }
    )
    args = {
        "meta": meta,
        "events": Event.objects.filter(
            is_deleted=False, is_published=True, community__subdomain=subdomain
        ).values(
            "id", "name", "start_date_and_time", "end_date_and_time", "featured_summary"
        ),
    }
    return render(request, "events.html", args)


def event(request, id):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    event = Event.objects.filter(
        is_deleted=False, is_published=True, pk=id, community__subdomain=subdomain
    ).first()

    if not event:
        raise Http404

    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(event),
        }
    )
    args = {
        "host": HOST,
        "event": event,
    }
    return render(request, "event.html", args)


def vendors(request):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    community = Community.objects.filter(
        subdomain__iexact=subdomain, is_deleted=False, is_published=True
    ).first()
    if not community:
        raise Http404

    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Services & Vendors",
        }
    )

    args = {
        "meta": meta,
        "vendors": community.community_vendors.filter(is_deleted=False).values(
            "id", "name", "description", "service_area"
        ),
    }
    return render(request, "services.html", args)


def vendor(request, id):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    vendor = Vendor.objects.filter(is_deleted=False, pk=id).first()

    if not vendor:
        raise Http404

    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(vendor),
        }
    )

    args = {
        "meta": meta,
        "vendor": vendor,
    }

    return render(request, "service.html", args)


def teams(request):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Teams",
        }
    )

    args = {
        "meta": meta,
        "teams": Team.objects.filter(
            is_deleted=False, is_published=True, community__subdomain=subdomain
        ).values("id", "name", "tagline"),
    }
    return render(request, "teams.html", args)


def team(request, id):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    team = Team.objects.filter(
        is_deleted=False, is_published=True, pk=id, community__subdomain=subdomain
    ).first()

    if not team:
        raise Http404

    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(team),
        }
    )

    args = {
        "meta": meta,
        "team": team,
    }
    return render(request, "team.html", args)


def testimonials(request):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": "Teams",
        }
    )

    args = {
        "meta": meta,
        "title": "Testimonials and User Stories",
        "testimonials": Testimonial.objects.filter(
            is_deleted=False, is_published=True, community__subdomain=subdomain
        ).values("id", "title", "body"),
    }
    return render(request, "testimonials.html", args)


def testimonial(request, id):
    subdomain = _get_subdomain(request, enforce_is_valid=True)
    testimonial = Testimonial.objects.filter(
        is_deleted=False, is_published=True, pk=id, community__subdomain=subdomain
    ).first()

    if not testimonial:
        raise Http404

    meta = META
    meta.update(
        {
            "subdomain": subdomain,
            "title": str(testimonial),
        }
    )

    args = {
        "meta": meta,
        "testimonial": testimonial,
    }
    return render(request, "testimonial.html", args)


def generate_sitemap(request):
    d = MiscellaneousStore().generate_sitemap_for_portal()
    return render(request, "sitemap_template.xml", d, content_type="text/xml")


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
