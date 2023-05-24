import time
import jwt
from http.cookies import SimpleCookie
from datetime import datetime, timedelta
from django.utils import timezone

from ..store.utils import unique_media_filename
from _main_.settings import SECRET_KEY
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagConstants
from database.models import (
    Action,
    Community,
    CommunityAdminGroup,
    CommunityMember,
    Event,
    FeatureFlag,
    Footage,
    HomePageSettings,
    Media,
    Message,
    RealEstateUnit,
    Team,
    Testimonial,
    UserActionRel,
    UserMediaUpload,
    UserProfile,
)
from carbon_calculator.models import CalcDefault
import requests
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

RESET = "reset"


def makeFootage(**kwargs):
    communities = kwargs.pop("communities",None)    
    f =  Footage.objects.create(**{**kwargs})
    if communities: 
        f.communities.set(communities)
    return f


def makeUserActionRel(**kwargs):
    action = kwargs.get("action")
    community = kwargs.pop("community", action.community)
    house = RealEstateUnit.objects.create(
        **{"name": str(time.time()) + "-house", "community": community}
    )
    return UserActionRel.objects.create(**{"real_estate_unit": house, **kwargs})


def makeTeam(**kwargs):
    name = kwargs.get("name", str(time.time()) + "-team")
    community = kwargs.pop("community", None)
    communities = kwargs.pop("communities", None)
    team = Team.objects.create(
        **{**kwargs, "primary_community": community, "name": name}
    )
    if communities:
        team.set(communities)
    return team


def makeMessage(**kwargs):
    user = kwargs.get("user")
    name = kwargs.pop("name", user.full_name)
    return Message.objects.create(**{**kwargs, "user_name": name})


def makeMembership(**kwargs):
    return CommunityMember.objects.create(**{**kwargs})


def makeFlag(**kwargs):
    name = kwargs.get("name") or "New Feature Flag"
    coms = kwargs.pop("communities", [])
    users = kwargs.pop("users", [])
    future_expiration = datetime.now(timezone.utc) + timedelta(days=3)
    flag = FeatureFlag.objects.create(
        **{
            "expires_on": future_expiration,
            "audience": FeatureFlagConstants.for_everyone(),
            "key": str(time.time()) + "-feature",
            **kwargs,
            "name": name,
        }
    )

    if coms:
        flag.communities.set(coms)
    if users:
        flag.users.set(users)

    return flag


def makeMedia(**kwargs):
    name = kwargs.get("name") or "New Media"
    file = kwargs.get("file") or kwargs.get("image") or createImage()
    file.name = unique_media_filename(file)
    return Media.objects.create(**{**kwargs, "name": name, "file": file})


def makeTestimonial(**kwargs):
    key = round(time.time() * 1000)
    title = kwargs.get("title") or kwargs.get("name") or f"New Testimonial - {key}"
    return Testimonial.objects.create(**{**kwargs, "title": title})


def makeEvent(**kwargs):
    community = kwargs.get("community")
    name = kwargs.get("name") or "Event default Name"
    pub_coms = kwargs.pop("communities_under_publicity", [])
    event = Event.objects.create(
        **{
            "is_published": True,
            "start_date_and_time": timezone.now()+ timezone.timedelta(days=1),
            "end_date_and_time": timezone.now() + timezone.timedelta(days=2),
            **kwargs,
            "community": community,
            "name": name,
        }
    )

    if pub_coms:
        event.communities_under_publicity.set(pub_coms)

    return event


def makeAction(**kwargs):
    community = kwargs.get("community")
    title = kwargs.get("title") or "Action default title"
    action = Action.objects.create(
        **{
            **kwargs,
            "community": community,
            "title": title,
        }
    )
    return action


def makeAdminGroup(**kwargs):
    key = round(time.time() * 1000)
    name = kwargs.get("name") or f"New Group - {key}"
    members = kwargs.pop("members")
    group, exists= CommunityAdminGroup.objects.get_or_create(**{**kwargs, "name": name})
    if members:
        group.members.set(members)

    return group


def makeAdmin(**kwargs):
    key = round(time.time() * 1000)
    communities = kwargs.pop("communities",[])
    full_name = kwargs.get("full_name") or f"user_full_name{key}"
    email = kwargs.get("email") or f"mrsadmin{key}@email.com"
    is_super_admin = kwargs.get("super_admin") or kwargs.get("is_super_admin")
    admin = UserProfile.objects.create(
        **{
            **kwargs,
            "full_name": full_name,
            "email": email,
            "accepts_terms_and_conditions": True,
            "is_community_admin": True,
            "is_super_admin": is_super_admin or False,
        }
    )
    if communities:
        for com in communities:
            makeAdminGroup(community=com, members=[admin])
    return admin


def makeUser(**kwargs):
    full_name = kwargs.pop("name", None) or kwargs.get("full_name") or "user_full_name"
    email = kwargs.get("email") or str(time.time()) + "@gmail.com"
    return UserProfile.objects.create(
        **{**kwargs, "full_name": full_name, "email": email}
    )


def makeUserUpload(**kwargs):
    media = kwargs.get("media") or makeMedia()
    communities = kwargs.get("communities")
    if communities:
        del kwargs["communities"]
    up = UserMediaUpload.objects.create(**{**kwargs, "media": media})
    if communities:
        up.communities.set(communities)
    return up


def makeHomePageSettings(**kwargs):
    title = kwargs.get("title") or str(time.time())
    community = kwargs.get(
        "community", makeCommunity(name="Default Community - For Homepage")
    )
    home = HomePageSettings.objects.create(
        **{
            **kwargs,
            "community": community,
            "title": title,
        }
    )

    return home


def makeCommunity(**kwargs):
    subdomain = kwargs.get("subdomain") or str(time.time())
    name = kwargs.get("name") or "community_default_name"
    com = Community.objects.create(
        **{
            "accepted_terms_and_conditions": True,
            "is_published": True,
            "is_approved": True,
            **kwargs,
            "subdomain": subdomain,
            "name": name,
        }
    )

    return com


def setupCC(client):
    cq = CalcDefault.objects.all()
    num = cq.count()
    if num <= 0:
        client.post(
            "/cc/import",
            {
                "Confirm": "Yes",
                "Actions": "carbon_calculator/content/Actions.csv",
                "Questions": "carbon_calculator/content/Questions.csv",
                "Stations": "carbon_calculator/content/Stations.csv",
                "Groups": "carbon_calculator/content/Groups.csv",
                "Organizations": "carbon_calculator/content/Organizations.csv",
                "Events": "carbon_calculator/content/Events.csv",
                "Defaults": "carbon_calculator/content/Defaults.csv",
            },
        )


def makeAuthToken(user):
    dt = datetime.now()
    dt.microsecond

    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "is_super_admin": user.is_super_admin,
        "is_community_admin": user.is_community_admin,
        "iat": dt.microsecond,
        "exp": dt.microsecond + 1000000000,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode("utf-8")


def signinAs(client, user):

    if user:
        the_token = makeAuthToken(user)

        client.cookies = SimpleCookie({"token": the_token})
        return the_token
    else:
        client.cookies = SimpleCookie({"token": ""})


def createUsers():

    user, created = UserProfile.objects.get_or_create(
        full_name="Regular User",
        email="no-reply@massenergize.org",
        accepts_terms_and_conditions=True,
    )
    if created:
        user.save()

    cadmin, created = UserProfile.objects.get_or_create(
        full_name="Community Admin",
        email="no-reply+1@massenergize.org",
        accepts_terms_and_conditions=True,
        is_community_admin=True,
    )
    if created:
        cadmin.save()

    sadmin, created = UserProfile.objects.get_or_create(
        full_name="Super Admin",
        email="no-reply+2@massenergize.org",
        accepts_terms_and_conditions=True,
        is_super_admin=True,
    )
    if created:
        sadmin.save()

    return user, cadmin, sadmin


def createImage(picURL=None):

    # this may break if that picture goes away.  Ha ha - keep you on your toes!
    if not picURL:
        picURL = "https://www.whitehouse.gov/wp-content/uploads/2021/04/P20210303AS-1901-cropped.jpg"

    resp = requests.get(picURL)
    if resp.status_code != requests.codes.ok:
        # Error handling here3
        print("ERROR: Unable to import image file from " + picURL)
        image_file = None
    else:
        image = resp.content
        file_name = picURL.split("/")[-1]
        file_type_ext = file_name.split(".")[-1]

        content_type = "image/jpeg"
        if len(file_type_ext) > 0 and file_type_ext.lower() == "png":
            content_type = "image/png"

        # Create a new Django file-like object to be used in models as ImageField using
        # InMemoryUploadedFile.  If you look at the source in Django, a
        # SimpleUploadedFile is essentially instantiated similarly to what is shown here
        img_io = BytesIO(image)
        image_file = InMemoryUploadedFile(
            img_io, None, file_name, content_type, None, None
        )

    return image_file
