from http.client import BAD_REQUEST
import os
from uuid import UUID
import html2text, traceback
from django.shortcuts import render, redirect
from _main_.utils.common import serialize_all
from _main_.utils.massenergize_errors import InvalidResourceError, ServerError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.http import Http404, JsonResponse
from _main_.settings import IS_PROD, IS_CANARY, RUN_SERVER_LOCALLY, EnvConfig
from _main_.utils.massenergize_logger import log
from api.decorators import x_frame_options_exempt
from api.handlers.misc import MiscellaneousHandler
from api.store.misc import MiscellaneousStore
from _main_.utils.constants import RESERVED_SUBDOMAIN_LIST, STATES
from api.utils.api_utils import get_distance_between_coords
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
from apps__campaigns.models import Campaign, CampaignTechnology
from django.db.models import Q
from django.template.loader import render_to_string
from _main_.utils.metrics import timed
import zipcodes
from _main_.utils.massenergize_logger import log

extract_text_from_html = html2text.HTML2Text()
extract_text_from_html.ignore_links = True

HOME_SUBDOMAIN_SET = set(
    [
        "communities",
        "communities-dev",
        "communities-canary",
        "search",
        "search-dev",
        "search-canary",
        "share",
        "share-dev",
        "share-canary",
    ]
)

IS_LOCAL = RUN_SERVER_LOCALLY  # API and community portal running locally
if IS_LOCAL:
    PORTAL_HOST = "http://massenergize.test:3000"
    CAMPAIGN_HOST = "http://localhost:3000"
elif IS_CANARY:
    PORTAL_HOST = "https://community-canary.massenergize.org"
    CAMPAIGN_HOST = "https://campaigns-canary.massenergize.org"
elif IS_PROD:
    PORTAL_HOST = "https://community.massenergize.org"
    CAMPAIGN_HOST = (
        "https://campaigns.massenergize.org"  # Change value when we have the appropriate link
    )
else:
    # we know it is dev
    PORTAL_HOST = "https://community.massenergize.dev"
    CAMPAIGN_HOST = "https://campaigns.massenergize.dev"  # Change value when we have the appropriate link


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
    "is_local": IS_LOCAL,
}

@x_frame_options_exempt
def rewiring_america(request):
    args  ={
        "rewiring_america": os.environ.get('REWIRING_AMERICA_API_KEY')
    }
    return render(request,"rewiring_america.html", args)

@timed
def campaign(request, campaign_id):

    campaign = None
    try:
        uuid_id = UUID(campaign_id, version=4)
        campaign = Campaign.objects.filter(id=uuid_id, is_deleted=False).first()
    except ValueError:
        campaign = Campaign.objects.filter(slug=campaign_id, is_deleted=False).first()
    if not campaign:
        raise Http404
    image = campaign.image.file.url

    redirect_url = f"{CAMPAIGN_HOST}{request.get_full_path()}"
    meta = {
            "image_url": _get_file_url(campaign.image),
            # "subdomain": subdomain,
            "title": campaign.title,
            "description": _extract(campaign.description),
            "url": f"{redirect_url}/actions/{id}",
            "redirect_to": redirect_url,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
            "stay_put": request.GET.get("stay_put", None),
        }
    # meta = {
    #     "title": campaign.title,
    #     "redirect_to": f"{CAMPAIGN_HOST}/campaign/{campaign.id}",
    #     "image": image,
    #     "image_url": image,
    #     "summary_large_image": image,
    #     "description": campaign.description,
    #     # "stay_put": True,
    # }
    args = {
        "meta": meta,
        "title": campaign.title,
        "id": campaign.id,
        "image": image,
        "campaign": campaign,
        "tagline": campaign.tagline,
    }
    return render(request, "campaign.html", args)


def campaign_technology(request, campaign_id, campaign_technology_id):
    camp_tech = CampaignTechnology.objects.filter(
        id=campaign_technology_id, is_deleted=False
    ).first()
    if not camp_tech or not campaign_technology_id or not campaign_id:
        raise Http404

    technology = camp_tech.technology
    image = _get_file_url(technology.image)

    redirect_url = f"{CAMPAIGN_HOST}{request.get_full_path()}"
    meta = {
        "image_url": image,
        # "subdomain": subdomain,
        "title": technology.name,
        "description": _extract(technology.description),
        "url": redirect_url,
        "redirect_to": redirect_url,
        "created_at": technology.created_at,
        "updated_at": technology.updated_at,
        "stay_put": request.GET.get("stay_put", None),
    }


    # meta = {
    #     "title": technology.name,
    #     "redirect_to":f"{CAMPAIGN_HOST}/campaign/{campaign_id}/technology/{campaign_technology_id}" ,
    #     "image": image,
    #     "image_url": image,
    #     "summary_large_image": image,
    #     "description": technology.description,
    #     "stay_put": True,
    # }
    args = {
        "meta": meta,
        "title": technology.name,
        "id": campaign_technology_id,
        "image": image,
    }
    return render(request, "campaign_technology.html", args)


def _restructure_communities(communities):
    _communities = []
    for community in communities:
        location = community.location
        prefix = ""
        if location:
            city = location.get("city")
            state = location.get("state")
            if state:
                for (
                    abbrev,
                    name,
                ) in (
                    STATES.items()
                ):  # for name, age in dictionary.iteritems():  (for Python 2.x)
                    if state.lower() == name.lower():
                        prefix = abbrev + " - "
            if city:
                prefix = city + ", " + prefix
        displayName = prefix + community.name
        _communities.append(
            {
                "id": community.id,
                "displayName": displayName,
                "subdomain": community.subdomain,
                "logo": _get_file_url(community.logo),
                "location": location,
            }
        )

    def sortFunc(e):
        return e.get("displayName", "").capitalize()

    _communities.sort(key=sortFunc)

    return _communities


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
                return False  # sandbox=false
        return False  # sandbox not specified
    return False  # no query string


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
        community=community
    ).first()
    if community_website_search:
        redirect_url = f"https://{community_website_search.website}"
    return redirect_url


def _base_community_query(is_sandbox):
    if is_sandbox:
        communityList = Community.objects.filter(is_deleted=False)
    else:
        communityList = Community.objects.filter(is_deleted=False, is_published=True)
    return communityList


def _get_file_url(image):
    if not image:
        return ""
    return image.file.url if image.file else ""


def _separate_communities(communities, lat, long):
    MAX_DISTANCE = 25
    close = []
    other = []
    if not communities:
        return close, other

    if not lat or not long:
        return close, communities

    for community in communities:
        if not community.is_geographically_focused:
            if community not in other:
                other.append(community)
            continue

        if not community.locations.all():
            if community not in other:
                other.append(community)

        for location in community.locations.all():
            if not location.zipcode:
                if community not in other:
                    other.append(community)
                continue
            
            try:
                community_zipcode_info = zipcodes.matching(location.zipcode)
                community_zipcode_lat = community_zipcode_info[0]["lat"]
                community_zipcode_long = community_zipcode_info[0]["long"]
            except ValueError as e:
                continue

            distance = get_distance_between_coords(
                float(lat),
                float(long),
                float(community_zipcode_lat),
                float(community_zipcode_long),
            )

            if distance < MAX_DISTANCE:
                if community not in close:
                    close.append(community)

            else:
                if community not in other:
                    other.append(community)
    return close, other

@timed
def home(request):
    subdomain = _get_subdomain(request, False)
    if not subdomain or subdomain in HOME_SUBDOMAIN_SET:
        return communities(request)
    elif _subdomain_is_valid(subdomain):
        return community(request, subdomain)

    return redirect(HOST)

def api_home(request):
    return MiscellaneousHandler().home(request)


@timed
def search_communities(request):
    exact = []
    other = []
    nearby = []
    meta = META
    meta.update(
        {
            "title": "Massenergize Communities",
            "redirect_to": f"{PORTAL_HOST}",
            "stay_put": True,
        }
    )
    query = request.POST.get("query")

    is_sandbox = _get_is_sandbox(request)
    base = _base_community_query(is_sandbox)

    if query:
        if not query.isdigit():
            exact = base.filter(Q(name__icontains=query))
        else:
            if zipcodes.is_real(query):
                exact = base.filter(locations__zipcode=query)
                zipcode_info = zipcodes.matching(query)
                zipcode_lat = zipcode_info[0]["lat"]
                zipcode_long = zipcode_info[0]["long"]
                nearby, _ = _separate_communities(
                    base.exclude(id__in=exact), zipcode_lat, zipcode_long
                )

    else:
        other = base

    args = {
        "meta": meta,
        "exact": _restructure_communities(exact),
        "other": _restructure_communities(other),
        "nearby": _restructure_communities(nearby),
        "sandbox": is_sandbox,
        "suffix": "?sandbox=true" if is_sandbox else "",
        "ready": True,
    }

    html = render_to_string(
        template_name="communities-results-partial.html", context=args
    )

    data_dict = {"html_from_view": html}
    return JsonResponse(data=data_dict, safe=False)

@timed
def communities(request):
    lat = request.POST.get("latitude")
    long = request.POST.get("longitude")
    meta = META
    meta.update(
        {
            "title": "Massenergize Communities",
            "redirect_to": f"{PORTAL_HOST}",
            "stay_put": True,
        }
    )

    is_sandbox = _get_is_sandbox(request)
    suffix = "?sandbox=true" if is_sandbox else ""

    communityList = _base_community_query(is_sandbox)

    near_by, other = _separate_communities(communityList, lat, long)

    args = {
        "meta": meta,
        "nearby": _restructure_communities(near_by),
        "other": _restructure_communities(other),
        "sandbox": is_sandbox,
        "suffix": suffix,
        "ready": True,
    }
    if lat and long:
        html = render_to_string(
            template_name="communities-results-partial.html", context=args
        )

        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
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
            "stay_put": request.GET.get("stay_put", None),
        }
    )

    args = {
        "meta": meta,
        "page": page,
    }

    return render(request, "page__contact_us.html", args)

def health_check(request):
    return MiscellaneousHandler().health_check(request)


def version(request):
    return MiscellaneousHandler().version(request)


def generate_sitemap(request):
    d = MiscellaneousStore().generate_sitemap_for_portal()
    return render(request, "sitemap_template.xml", d, content_type="text/xml")


def generate_sitemap_main(request):
    d = MiscellaneousStore().generate_sitemap_for_portal()
    return render(request, "sitemap_template_new.xml", d, content_type="text/xml")


def handler400(request, exception):
    log.error(
        exception=str(exception),
        extra={
            'status_code': 400,
            'request_path': request.path
        }
    )
    return MassenergizeResponse(error=str(exception))


def handler403(request, exception):
    log.error(
        exception=str(exception),
        extra={
            'status_code': 403,
            'request_path': request.path
        }
    )
    return MassenergizeResponse(error=str(exception.msg))


def handler404(request, exception):
    log.error(
        exception=str(exception),
        extra={
            'status_code': InvalidResourceError().status_code,
            'request_path': request.path
        }
    )

    return MassenergizeResponse(error=str(exception))


def handler500(request):
    err = ServerError()
    log.error(
        message=err.msg,
        extra={
            'status_code': err.status_code,
            'request_path': request.path
        }
    )
    return MassenergizeResponse(error=err.msg)
