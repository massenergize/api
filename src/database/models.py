import datetime
import json
import uuid
from datetime import timezone, timedelta

from _main_.utils.common import item_is_empty

from _main_.utils.policy.PolicyConstants import PolicyConstants
from _main_.utils.base_model import BaseModel
from _main_.utils.base_model import RootModel
from apps__campaigns.helpers import get_user_accounts
from database.utils.settings.model_constants.events import EventConstants
from django.db import models
from django.db.models.fields import BooleanField
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagConstants
from _main_.utils.footage.FootageConstants import FootageConstants
from database.utils.constants import *
from database.utils.settings.admin_settings import AdminPortalSettings
from database.utils.settings.model_constants.user_media_uploads import (
    UserMediaConstants,
)
from database.utils.settings.user_settings import UserPortalSettings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.db.models.query import QuerySet

from .utils.common import (
    get_images_in_sequence,
    json_loader,
    get_json_if_not_none,
    get_summary_info,
    make_hash_from_file,
)
from api.constants import COMMUNITY_NOTIFICATION_TYPES, STANDARD_USER, GUEST_USER
from django.forms.models import model_to_dict
from carbon_calculator.models import Action as CCAction
from carbon_calculator.carbonCalculator import AverageImpact
from .utils.settings.model_constants.enums import SharingType, LocationType

CHOICES = json_loader("./database/raw_data/other/databaseFieldChoices.json")
ZIP_CODE_AND_STATES = json_loader("./database/raw_data/other/states.json")

# -------------------------------------------------------------------------


def get_enabled_flags(
    _self, users=False
):  # _self : CommunityObject or UserProfileObject
    feature_flags = FeatureFlag.objects.all()  # We get all available flags
    feature_flags_json = []
    for f in feature_flags:  # Go over all the flags
        specified = (
            f.communities.all() if not users else f.users.all()
        )  # Then note down which communities each flag is enabled for
        enabled = (
            (f.audience == "EVERYONE")
            or (  # FeatureFlagConstants.AUDIENCE["EVERYONE"]["key"]
                f.audience == "SPECIFIC" and _self in specified
            )
            or (f.audience == "ALL_EXCEPT" and _self not in specified)
        )  # Check if flag is enabled for the community
        enabled = enabled and (
            not f.expires_on
            or f.expires_on > datetime.datetime.now(f.expires_on.tzinfo)
        )
        if enabled:
            feature_flags_json.append(
                f.info()
            )  # Then if the flag hasnt expired, note down the flag
    return feature_flags_json


def user_is_due_for_mou(user):
    """
    Returns user policy acceptance status

    Args:
        user (UserProfile): The User Profile to check for policy

        last_record (PolicyAcceptanceRecords|None): Latest Policy Acceptance Record or None if there is none
    """
    a_year_ago = datetime.datetime.now(timezone.utc) - timedelta(days=365)

    try:
        last_record = PolicyAcceptanceRecords.objects.filter(
            user=user, type=PolicyConstants.mou()
        ).latest("signed_at")
    except PolicyAcceptanceRecords.DoesNotExist:
        return True, None

    # ok if user signed MOU after the date one year ago
    if last_record.signed_at and last_record.signed_at > a_year_ago:
        return False, last_record.simple_json()

    return True, last_record.simple_json()


def fetch_few_visits(user):
    footages = Footage.objects.filter(
        actor__id=user.id,
        activity_type=FootageConstants.sign_in(),
        portal=FootageConstants.on_user_portal(),
    ).values_list("created_at", flat=True)[:5]
    if len(footages):
        return list(footages)

    visits = user.visit_log or []
    return visits[-5:]


# -------------------------------------------------------------------------
class Location(models.Model):
    """
    A class used to represent a geographical region.  It could be a complete and
    proper address or just a city name, zipcode, county etc

    Attributes
    ----------
    type : str
      the type of the location, whether it is a full address, zipcode only, etc
    street : str
      The street number if it is available
    city : str
      the name of the city if available
    county : str
      the name of the county if available
    state: str
      the name of the state if available
    more_info: JSON
      any anotheraction() dynamic information we would like to store about this location
    """

    id = models.AutoField(primary_key=True)
    location_type = models.CharField(
        max_length=TINY_STR_LEN, choices=CHOICES.get("LOCATION_TYPES", {}).items()
    )
    street = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    unit_number = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    zipcode = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    city = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    county = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    state = models.CharField(max_length=SHORT_STR_LEN, choices=ZIP_CODE_AND_STATES.items(), blank=True)
    country = models.CharField(max_length=SHORT_STR_LEN, default="US", blank=True)
    more_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        # show full loc regardless of tye type its labelled as
        loc = ""
        d = lambda: ", " if loc != "" else ""
        if self.street:
            loc += self.street
        if self.unit_number:
            loc += d() + "#" + self.unit_number
        if self.city:
            loc += d() + self.city
        if self.zipcode:
            loc += d() + self.zipcode
        if self.county:
            loc += d() + self.county
        if self.state:
            loc += d() + self.state
        if self.country and self.country != "US":
            loc += d() + self.country
        loc += "-" + self.location_type
        return loc

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class TranslationMeta:
        fields_to_translate = []

    class Meta:
        db_table = "locations"

class TagCollection(models.Model):
    """
    A class used to represent a collection of Tags.

    Attributes
    ----------
    name : str
      name of the Tag Collection
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
    is_global = models.BooleanField(default=False, blank=True)
    allow_multiple = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)
    rank = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def simple_json(self):
        res = model_to_dict(self)
        res["tags"] = [t.simple_json() for t in self.tag_set.all()]
        return res

    def full_json(self):
        return self.simple_json()

    class TranslationMeta:
        fields_to_translate = []

    class Meta:
        ordering = ("name",)
        db_table = "tag_collections"


class Tag(models.Model):
    """
    A class used to represent an Tag.  It is essentially a string that can be
    used to describe or group items, actions, etc

    Attributes
    ----------
    name : str
      name of the Tag
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    points = models.PositiveIntegerField(null=True, blank=True)
    icon = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    tag_collection = models.ForeignKey(
        TagCollection, null=True, on_delete=models.CASCADE, blank=True
    )
    rank = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "%s - %s" % (self.name, self.tag_collection)

    def info(self):
        return model_to_dict(self, ["id", "name"])

    def simple_json(self):
        res = model_to_dict(self)
        res["order"] = self.rank
        res["tag_collection_name"] = (
            None if not self.tag_collection else self.tag_collection.name
        )
        return res

    def full_json(self):
        data = self.simple_json()
        data["tag_collection"] = get_json_if_not_none(self.tag_collection)
        return data

    class TranslationMeta:
        fields_to_translate = ["name"]

    class Meta:
        ordering = ("rank",)
        db_table = "tags"
        unique_together = [["rank", "name", "tag_collection"]]


class Media(models.Model):
    """
    A class used to represent any Media that is uploaded to this website

    Attributes
    ----------
    name : SlugField
      The short name for this media.  It cannot only contain letters, numbers,
      hypens and underscores.  No spaces allowed.
    file : File
      the file that is to be stored.
    media_type: str
      the type of this media file whether it is an image, video, pdf etc.
    """

    id = models.AutoField(primary_key=True)
    name = models.SlugField(max_length=SHORT_STR_LEN, blank=True)
    file = models.FileField(upload_to="media/")
    media_type = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="media_tags", blank=True)
    hash = models.TextField(max_length=LONG_STR_LEN, blank=True, db_index=True)

    def __str__(self):
        return str(self.id) + "-" + self.name + "(" + self.file.name + ")"

    def info(self):
        return self.simple_json()

    def simple_json(self):
        obj = {
            "id": self.id,
            "name": self.name,
            "url": self.file.url,
        }
        if hasattr(self, "user_upload"):
            obj["created_at"] = self.user_upload.created_at
            obj["info"] = self.user_upload.info

        return obj

    def full_json(self):
        return {
            **self.simple_json(),
            "id": self.id,
            "name": self.name,
            "url": self.file.url,
            "media_type": self.media_type,
            "tags": [tag.simple_json() for tag in self.tags.all()],
        }

    def delete(self, *args, **kwargs):
        # Overriding the default delete fxn to delete actual file from  storage as well
        if self.file:
            file_path = self.file.name
            default_storage.delete(file_path)

        super().delete(*args, **kwargs)

    def calculate_hash(self, uploaded_file):
        if not self.hash:
            image_data = uploaded_file.read()
            calculated_hash =  make_hash_from_file(image_data)
            return calculated_hash
        return None

    def save(self, *args, **kwargs):
        if self.file and not self.hash:
            hash = self.calculate_hash(self.file.file)
            if hash:
                self.hash = hash
        super().save(*args, **kwargs)

    def get_s3_key(self):
        return self.file.name

    class TranslationMeta:
        fields_to_translate = []

    class Meta:
        db_table = "media"
        ordering = ("order", "-id")


class Policy(models.Model):
    """
     A class used to represent a Legal Policy.  For instance the
     Terms and Agreement Statement that users have to agree to during sign up.


    Attributes
    ----------
    name : str
      name of the Legal Policy
    description: str
      the details of this policy
    communities_applied:
      how many communities this policy applies to.
    is_global: boolean
      True if this policy should apply to all the communities
    info: JSON
      dynamic information goes in here
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=LONG_STR_LEN, db_index=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    is_global = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    more_info = models.JSONField(blank=True, null=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        res = model_to_dict(self)
        more_info = self.more_info or {}
        res["key"] = more_info.get("key", "")
        return res

    def full_json(self):
        # would this blow up because no community_set?
        # community_policies is a related_name on the community table
        res = self.simple_json()
        community = self.community_policies.all().first()
        if community:
            res["community"] = get_json_if_not_none(community)
        return res

    class TranslationMeta:
        fields_to_translate = ["name", "description"]

    class Meta:
        ordering = ("name",)
        db_table = "legal_policies"
        verbose_name_plural = "Legal Policies"


class Goal(models.Model):
    """
    A class used to represent a Goal

    Attributes
    ----------
    name : str
      A short title for this goal
    status: str
      the status of this goal whether it has been achieved or not.
    description:
      More details about this goal
    target_date:
      Date at which goal should be achieved
    created_at: DateTime
      The date and time that this goal was added
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this goal
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)

    target_number_of_households = models.PositiveIntegerField(default=0, blank=True)
    target_number_of_actions = models.PositiveIntegerField(default=0, blank=True)
    target_carbon_footprint_reduction = models.PositiveIntegerField(
        default=0, blank=True
    )

    initial_number_of_households = models.PositiveIntegerField(default=0, blank=True)
    initial_number_of_actions = models.PositiveIntegerField(default=0, blank=True)
    initial_carbon_footprint_reduction = models.PositiveIntegerField(
        default=0, blank=True
    )

    attained_number_of_households = models.PositiveIntegerField(default=0, blank=True)
    attained_number_of_actions = models.PositiveIntegerField(default=0, blank=True)
    attained_carbon_footprint_reduction = models.PositiveIntegerField(
        default=0, blank=True
    )

    organic_attained_number_of_households = models.PositiveIntegerField(
        default=0, blank=True
    )
    organic_attained_number_of_actions = models.PositiveIntegerField(
        default=0, blank=True
    )
    organic_attained_carbon_footprint_reduction = models.PositiveIntegerField(
        default=0, blank=True
    )

    target_date = models.DateField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    more_info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.name} {' - Deleted' if self.is_deleted else ''}"

    def simple_json(self):
        return model_to_dict(self, exclude=["is_deleted"])

    def full_json(self):
        return self.simple_json()

    class TranslationMeta:
        fields_to_translate = ["name", "description"]

    class Meta:
        db_table = "goals"


class Community(models.Model):
    """
    A class used to represent a Community on this platform.

    Attributes
    ----------
    name : str
      The short name for this Community
    subdomain : str (can only contain alphabets, numbers, hyphen and underscores)
      a primary unique identifier for this Community.  They would need the same
      to access their website.  For instance if the subdomain is wayland they
      would access their portal through wayland.massenergize.org
    owner: JSON
      information about the name, email and phone of the person who is supposed
      to be owner and main administrator when this Community account is opened.
    logo : int
      Foreign Key to Media that holds logo of community
    banner : int
      Foreign Key to Media that holds logo of community
    is_geographically_focused: boolean
      Information about whether this community is geographically focused or
      dispersed
    is_approved: boolean
      This field is set to True if the all due diligence has been done by the
      Super Admins and the community is not allowed to operate.
    created_at: DateTime
      The date and time that this community was created
    policies: ManyToMany
      policies created by community admins for this community
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this community
    more_info: JSON
      any another dynamic information we would like to store about this location

    contact_info: JSON
       looks like this {"is_validated":bool , "nudge_count":int ,"sender_signature_id":str}
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    subdomain = models.SlugField(max_length=SHORT_STR_LEN, unique=True, db_index=True)
    owner_name = models.CharField(max_length=SHORT_STR_LEN, default="Unknown")
    owner_email = models.EmailField(blank=False)
    contact_sender_alias = models.CharField(
        blank=True, null=True, max_length=SHORT_STR_LEN
    )
    owner_phone_number = models.CharField(
        blank=True, null=True, max_length=SHORT_STR_LEN
    )
    about_community = models.TextField(max_length=LONG_STR_LEN, blank=True)
    logo = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="community_logo",
    )
    banner = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="community_banner",
    )
    favicon = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="community_favicon",
    )
    goal = models.ForeignKey(Goal, blank=True, null=True, on_delete=models.SET_NULL)

    is_geographically_focused = models.BooleanField(default=False, blank=True)

    # deprecated: location of community was originally a JSON string; now defined below in locations (link to Location model)
    location = models.JSONField(blank=True, null=True)

    # new - define the geographic area for a community (zipcodes, towns/cities, counties, states, countries)
    geography_type = models.CharField(
        max_length=TINY_STR_LEN,
        choices=CHOICES.get("COMMUNITY_GEOGRAPHY_TYPES", {}).items(),
        blank=True,
        null=True,
    )

    # locations defines the range for geographic communities
    locations = models.ManyToManyField(Location, blank=True)

    policies = models.ManyToManyField(
        Policy, blank=True, related_name="community_policies"
    )
    is_approved = models.BooleanField(default=False, blank=True)
    accepted_terms_and_conditions = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    more_info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)
    is_demo = models.BooleanField(default=False, blank=True)
    contact_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + " - " + self.name

    def info(self):
       res = model_to_dict(self, ["id", "name", "subdomain", "is_geographically_focused"])
       res["logo"] = get_json_if_not_none(self.logo)
       return res

    def get_logo_link_from_menu(self):
        menu = Menu.objects.filter(community=self, is_published=True)
        if menu:
            return menu.first().community_logo_link
        return None

    def simple_json(self):
        res = model_to_dict(
            self,
            [
                "id",
                "name",
                "subdomain",
                "owner_phone_number",
                "owner_name",
                "owner_email",
                "is_geographically_focused",
                "is_published",
                "is_approved",
                "more_info",
                "location",
                "contact_info",
                # "contact_sender_alias"
            ],
        )
        res["logo"] = get_json_if_not_none(self.logo)
        res["favicon"] = get_json_if_not_none(self.favicon)
        res["community_logo_link"] = self.get_logo_link_from_menu()
        res["feature_flags"] = get_enabled_flags(self)
        return res

    # def medium_json(self):
    #    res = self.simple_json()
    #    res["feature_flags"] =  get_enabled_flags(self)
    #    return res

    def full_json(self):
        admin_group: CommunityAdminGroup = CommunityAdminGroup.objects.filter(
            community__id=self.pk
        ).first()
        if admin_group:
            #admins = [a.simple_json() for a in admin_group.members.all()]
            admins = [a.info() for a in admin_group.members.all()]
        else:
            admins = []

        customDomain: CustomCommunityWebsiteDomain = (
            CustomCommunityWebsiteDomain.objects.filter(community__id=self.pk)
        )
        website = None
        if customDomain:
            website = customDomain.first().website

        # get the community goal
        goal = get_json_if_not_none(self.goal) or {}

        # goal defined consistently; not differently in two places
        if self.is_geographically_focused:
            goal[
                "organic_attained_number_of_households"
            ] = RealEstateUnit.objects.filter(is_deleted=False, community=self).count()
            done_actions = UserActionRel.objects.filter(
                real_estate_unit__community=self, status="DONE"
            ).prefetch_related("action__calculator_action")
        else:
            community_members = CommunityMember.objects.filter(
                is_deleted=False, community=self
            ).select_related("user")
            users = [cm.user for cm in community_members]
            members_count = community_members.count()
            goal["organic_attained_number_of_households"] = members_count
            done_actions = UserActionRel.objects.filter(
                user__in=users, status="DONE"
            ).prefetch_related("action__calculator_action")

        goal["organic_attained_number_of_actions"] = done_actions.count()

        carbon_footprint_reduction = 0
        for actionRel in done_actions:
            if actionRel.action and actionRel.action.calculator_action:
                carbon_footprint_reduction += AverageImpact(
                    actionRel.action.calculator_action, actionRel.date_completed
                )

        goal["organic_attained_carbon_footprint_reduction"] = carbon_footprint_reduction

        # calculate values for community impact to be displayed on front-end sites
        impact_page_settings: ImpactPageSettings = ImpactPageSettings.objects.filter(
            community__id=self.pk
        ).first()
        if impact_page_settings:
            display_prefs = impact_page_settings.more_info or {}
        else:
            # log.error("Impact Page Settings not found", level="error")
            display_prefs = {}  # not usual - show nothing

        value = 0
        if display_prefs.get("manual_households", True):
            value += goal.get("initial_number_of_households", 0)
        if display_prefs.get("state_households", False):
            value += goal.get("attained_number_of_households", 0)
        if display_prefs.get("platform_households", True):
            value += goal.get("organic_attained_number_of_households", 0)
        goal["displayed_number_of_households"] = value

        value = 0
        if display_prefs.get("manual_actions", False):
            value += goal.get("initial_number_of_actions", 0)
        if display_prefs.get("state_actions", True):
            value += goal.get("attained_number_of_actions", 0)
        if display_prefs.get("platform_actions", True):
            value += goal.get("organic_attained_number_of_actions", 0)
        goal["displayed_number_of_actions"] = value

        value = 0
        if display_prefs.get("manual_carbon", False):
            value += goal.get("initial_carbon_footprint_reduction", 0)
        if display_prefs.get("state_carbon", False):
            value += goal.get("attained_carbon_footprint_reduction", 0)
        if display_prefs.get("platform_carbon", True):
            value += goal.get("organic_attained_carbon_footprint_reduction", 0)
        goal["displayed_carbon_footprint_reduction"] = value

        locations = ""
        for loc in self.locations.all():
            if locations != "":
                locations += ", "
            if self.geography_type == "ZIPCODE":
                l = loc.zipcode
            elif self.geography_type == "CITY":
                l = loc.city
            elif self.geography_type == "COUNTY":
                l = loc.county
            elif self.geography_type == "STATE":
                l = loc.state
            elif self.geography_type == "COUNTRY":
                l = loc.country
            else:
                l = loc.zipcode
            locations += l

        # Feature flags can either enable features for specific communities, or disable them
        # feature_flags = FeatureFlag.objects.all()
        # feature_flags_json = []
        # for f in feature_flags:
        #     specified_communities = f.communities.all()
        #     enabled = (
        #         (f.audience == "EVERYONE")
        #         or (  # FeatureFlagConstants.AUDIENCE["EVERYONE"]["key"]
        #             f.audience == "SPECIFIC" and self in specified_communities
        #         )
        #         or (f.audience == "ALL_EXCEPT" and self not in specified_communities)
        #     )
        #     enabled = enabled and (
        #         not f.expires_on
        #         or f.expires_on > datetime.datetime.now(f.expires_on.tzinfo)
        #     )
        #     if enabled:
        #         feature_flags_json.append(f.simple_json())
        return {
            "id": self.id,
            "name": self.name,
            "subdomain": self.subdomain,
            "website": website,
            "owner_name": self.owner_name,
            "owner_email": self.owner_email,
            "owner_phone_number": self.owner_phone_number,
            "goal": goal,
            "about_community": self.about_community,
            "logo": get_json_if_not_none(self.logo),
            "favicon": get_json_if_not_none(self.favicon),
            "location": self.location,
            "is_approved": self.is_approved,
            "is_published": self.is_published,
            "is_geographically_focused": self.is_geographically_focused,
            "banner": get_json_if_not_none(self.banner),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "more_info": self.more_info,
            "admins": admins,
            "geography_type": self.geography_type,
            "locations": locations,
            "feature_flags": get_enabled_flags(self),
            "is_demo": self.is_demo,
            "contact_sender_alias": self.contact_sender_alias,
            "community_logo_link": self.get_logo_link_from_menu(),
        }

    class TranslationMeta:
        fields_to_translate = ["about_community"]

    class Meta:
        verbose_name_plural = "Communities"
        db_table = "communities"


class CommunitySnapshot(models.Model):
    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(
        Community, null=True, on_delete=models.SET_NULL, blank=True
    )
    date = models.DateField(auto_now_add=True, db_index=True)
    is_live = models.BooleanField(default=False, blank=True)
    households_total = models.PositiveIntegerField(default=0, blank=True)
    households_user_reported = models.PositiveIntegerField(default=0, blank=True)
    households_manual_addition = models.PositiveIntegerField(default=0, blank=True)
    households_partner = models.PositiveIntegerField(default=0, blank=True)
    primary_community_users_count = models.PositiveIntegerField(default=0, blank=True)
    member_count = models.PositiveIntegerField(default=0, blank=True)
    actions_live_count = models.PositiveIntegerField(default=0, blank=True)
    actions_total = models.PositiveIntegerField(default=0, blank=True)
    actions_partner = models.PositiveIntegerField(default=0, blank=True)
    actions_user_reported = models.PositiveIntegerField(default=0, blank=True)
    carbon_total = models.FloatField(default=0, blank=True)
    carbon_user_reported = models.FloatField(default=0, blank=True)
    carbon_manual_addition = models.FloatField(default=0, blank=True)
    carbon_partner = models.FloatField(default=0, blank=True)

    guest_count = models.PositiveIntegerField(default=0, blank=True)
    actions_manual_addition = models.PositiveIntegerField(default=0, blank=True)
    events_hosted_current = models.PositiveIntegerField(default=0, blank=True)
    events_hosted_past = models.PositiveIntegerField(default=0, blank=True)
    my_events_shared_current = models.PositiveIntegerField(default=0, blank=True)
    my_events_shared_past = models.PositiveIntegerField(default=0, blank=True)
    events_borrowed_from_others_current = models.PositiveIntegerField(
        default=0, blank=True
    )
    events_borrowed_from_others_past = models.PositiveIntegerField(
        default=0, blank=True
    )

    teams_count = models.PositiveIntegerField(default=0, blank=True)
    subteams_count = models.PositiveIntegerField(default=0, blank=True)
    testimonials_count = models.PositiveIntegerField(default=0, blank=True)
    service_providers_count = models.PositiveIntegerField(default=0, blank=True)

    def simple_json(self):
        res = model_to_dict(self)
        return res

    def full_json(self):
        return self.simple_json()

    def __str__(self):
        return " %s | %s " % (
            self.community,
            self.date,
        )

    class TranslationMeta:
        fields_to_translate = []

    class Meta:
        db_table = "community_snapshots"


class RealEstateUnit(models.Model):
    """
    A class used to represent a Real Estate Unit.

    Attributes
    ----------
    unit_type : str
      The type of this unit eg. Residential, Commercial, etc
    location: Location
      the geographic address or location of this real estate unit
    created_at: DateTime
      The date and time that this real estate unity was added
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this real estate unit
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    unit_type = models.CharField(
        max_length=TINY_STR_LEN, choices=CHOICES.get("REAL_ESTATE_TYPES", {}).items()
    )
    community = models.ForeignKey(
        Community, null=True, on_delete=models.SET_NULL, blank=True
    )
    location = models.JSONField(blank=True, null=True)
    # added 1/28/21 - redundant to location, address will have Zip code, defining which community the REU is in
    address = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def is_commercial(self):
        return self.unit_type == "C"

    def is_residential(self):
        return self.unit_type == "R"

    def __str__(self):
        return f"{self.community}|{self.unit_type}|{self.name}"

    def simple_json(self):
        # return model_to_dict(self)

        res = model_to_dict(self)
        res["location"] = get_json_if_not_none(self.address)
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "real_estate_units"

    class TranslationMeta:
        fields_to_translate = []


class Role(models.Model):
    """
    A class used to represent  Role for users on the MassEnergize Platform

    Attributes
    ----------
    name : str
      name of the role
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=TINY_STR_LEN,
        choices=CHOICES.get("ROLE_TYPES", {}).items(),
        unique=True,
    )
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return CHOICES.get("ROLE_TYPES", {})[self.name]

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ("name",)
        db_table = "roles"

    class TranslationMeta:
        fields_to_translate = ["name", "description"]


class UserProfile(models.Model):
    """
    A class used to represent a MassEnergize User

    Note: Authentication is handled by firebase so we just need emails

    Attributes
    ----------
    email : str
      email of the user.  Should be unique.
    user_info: JSON
      a JSON representing the name, bio, etc for this user.
    bio:
      A short biography of this user
    is_super_admin: boolean
      True if this user is an admin False otherwise
    is_community_admin: boolean
      True if this user is an admin for a community False otherwise
    is_vendor: boolean
      True if this user is a vendor False otherwise
    other_info: JSON
      any another dynamic information we would like to store about this UserProfile
    created_at: DateTime
      The date and time that this goal was added
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this goal

    notification_dates: dates that certain notifications were dispatched. It will probably look like
        notification_dates={
            "cadmin_nudge":"02/10/22",
            ** some other form of notification
        }

    #TODO: roles field: if we have this do we need is_superadmin etc? also why
    #  not just one?  why many to many
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    full_name = models.CharField(max_length=SHORT_STR_LEN, null=True)
    profile_picture = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="profile_picture",
    )
    preferred_name = models.CharField(max_length=SHORT_STR_LEN, null=True)
    email = models.EmailField(unique=True, db_index=True)
    user_info = models.JSONField(blank=True, null=True)
    real_estate_units = models.ManyToManyField(
        RealEstateUnit, related_name="user_real_estate_units", blank=True
    )
    goal = models.ForeignKey(Goal, blank=True, null=True, on_delete=models.SET_NULL)
    communities = models.ManyToManyField(Community, blank=True)
    roles = models.ManyToManyField(Role, blank=True)
    is_super_admin = models.BooleanField(default=False, blank=True)
    is_community_admin = models.BooleanField(default=False, blank=True)
    is_vendor = models.BooleanField(default=False, blank=True)
    other_info = models.JSONField(blank=True, null=True)
    accepts_terms_and_conditions = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    preferences = models.JSONField(default=dict, null=True, blank=True)
    visit_log = models.JSONField(default=list, null=True, blank=True)
    notification_dates = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return self.email

    def info(self):
        data = model_to_dict(self, ["id", "email", "full_name", "preferred_name"])
        data["profile_picture"] = get_json_if_not_none(self.profile_picture)
        return data

    def summary(self):
        summaryData = model_to_dict(self, ["preferred_name", "is_guest", "email"])
        summaryData["joined"] = self.created_at.date()
        summaryData["profile_picture"] = get_json_if_not_none(self.profile_picture)

        done_actions = UserActionRel.objects.filter(
            user=self, status="DONE"
        ).prefetch_related("action__calculator_action")
        done_points = 0
        for actionRel in done_actions:
            if actionRel.action and actionRel.action.calculator_action:
                done_points += AverageImpact(actionRel.action.calculator_action, actionRel.date_completed)
            else:
                done_points += actionRel.carbon_impact

        todo_actions = UserActionRel.objects.filter(
            user=self, status="TODO"
        ).prefetch_related("action__calculator_action")
        todo_points = 0
        for actionRel in todo_actions:
            if actionRel.action and actionRel.action.calculator_action:
                todo_points += AverageImpact(actionRel.action.calculator_action, actionRel.date_completed)
            else:
                todo_points += actionRel.carbon_impact

        user_testimonials = Testimonial.objects.filter(
            is_deleted=False, is_approved=True, user=self
        )
        testimonials_count = user_testimonials.count() if user_testimonials else "0"

        teams = Team.objects.filter(is_deleted=False, is_published=True)
        user_teams = teams.filter(teammember__user=self).values_list(
            "name", "teammember__is_admin"
        )

        teams_count = 0
        teams_led = 0
        team_names = []
        for team_name, is_admin in user_teams:
            team_names.append((team_name + "(ADMIN)") if is_admin else team_name)
            teams_count += 1
            if is_admin:
                teams_led += 1

        summaryData["actions_done"] = done_actions.count()
        summaryData["actions_done_points"] = done_points
        summaryData["actions_todo"] = todo_actions.count()
        summaryData["actions_todo_points"] = todo_points
        summaryData["teams_count"] = teams_count
        summaryData["teams_led"] = teams_led
        summaryData["teams"] = team_names
        summaryData["testimonials"] = testimonials_count

        return summaryData

    def simple_json(self):
        res = model_to_dict(
            self,
            [
                "id",
                "full_name",
                "preferred_name",
                "email",
                "is_super_admin",
                "is_community_admin",
            ],
        )
        res["joined"] = self.created_at.date()
        res["user_info"] = self.user_info
        res["profile_picture"] = get_json_if_not_none(self.profile_picture)
        res["communities"] = [
            c.community.name for c in CommunityMember.objects.filter(user=self)
        ]
        res["households"] = [h.simple_json() for h in self.real_estate_units.all()]

        is_guest = False
        if self.user_info:
            is_guest = self.user_info.get("user_type", STANDARD_USER) == GUEST_USER
        res["is_guest"] = is_guest

        preferences = self.preferences or {}
        user_portal_settings = (
            preferences.get("user_portal_settings") or UserPortalSettings.Defaults
        )
        admin_portal_settings = (
            preferences.get("admin_portal_settings") or AdminPortalSettings.Defaults
        )
        res["preferences"] = {
            **preferences,
            "user_portal_settings": user_portal_settings,
            "admin_portal_settings": admin_portal_settings,
        }
        res["accepts_terms_and_conditions"] = self.accepts_terms_and_conditions

        res["user_portal_visits"] = fetch_few_visits(self)
        return res

    def update_visit_log(self, date_time):
        try:
            new_format = "%Y/%m/%d"
            date = date_time.strftime(new_format)

            # We adapt the old fomat to the new one
            if type(self.visit_log) == dict:
                old = self.visit_log
                new = []
                for day in old.keys():
                    old_format = "%d/%m/%Y"
                    if len(day) < 10:
                        old_format = "%d/%m/%y"
                    dt_object = datetime.datetime.strptime(day, old_format)
                    day = dt_object.strftime(new_format)
                    new.append(day)
                self.visit_log = new

            if type(self.visit_log) == list:
                if len(self.visit_log) > 0:
                    if date != self.visit_log[-1]:
                        self.visit_log.append(date)
                else:
                    self.visit_log.append(date)
        except Exception as e:
            print(e)
            return None, e

    def full_json(self):
        team_members = [t.team.simple_json() for t in TeamMember.objects.filter(user=self)]
        community_members = CommunityMember.objects.filter(user=self)
        communities = [cm.community.info() for cm in community_members]
        data = model_to_dict(
            self, exclude=["real_estate_units", "communities", "roles"]
        )
        data["joined"] = self.created_at.date()
        admin_at = [
            get_json_if_not_none(c.community)
            for c in self.communityadmingroup_set.all()
        ]
        data["households"] = [h.simple_json() for h in self.real_estate_units.all()]
        data["goal"] = get_json_if_not_none(self.goal)
        data["communities"] = communities
        data["admin_at"] = admin_at
        data["teams"] = team_members
        data["profile_picture"] = get_json_if_not_none(self.profile_picture)
        data["visit_log"] = self.visit_log

        is_guest = False
        if self.user_info:
            is_guest = self.user_info.get("user_type", STANDARD_USER) == GUEST_USER
        data["is_guest"] = is_guest

        preferences = self.preferences or {}
        user_portal_settings = (
            preferences.get("user_portal_settings") or UserPortalSettings.Defaults
        )
        admin_portal_settings = (
            preferences.get("admin_portal_settings") or AdminPortalSettings.Defaults
        )
        data["preferences"] = {
            **preferences,
            "user_portal_settings": user_portal_settings,
            "admin_portal_settings": admin_portal_settings,
        }
        data["feature_flags"] = get_enabled_flags(self, True)
        if self.is_community_admin:
            mou_details = user_is_due_for_mou(self)
            data["needs_to_accept_mou"] = mou_details[0]
            data["mou_details"] = mou_details[1]
        # get campaign accounts created or admin of
        data["campaign_accounts"] = get_user_accounts(self)

        return data

    class Meta:
        db_table = "user_profiles"
        ordering = ("-created_at",)

    class TranslationMeta:
        fields_to_translate = []


class PolicyAcceptanceRecords(models.Model):
    """
     This model represents the user's acceptance of policies. It has the following fields:
    "user": a foreign key to the UserProfile model, which is set to null when the UserProfile is deleted.
    "signed_at": a DateTimeField that stores the date and time when the user accepted the policy.
    "last_notified": a JSON field that stores the last notification sent to the user about the policy, if applicable.
    "type": a CharField that stores the type of policy being accepted, defaulting to "MOU" (Memorandum of Understanding) if not specified. It could be anything depending on any new future scenarios where we need users to sign/accept other things that are not MOUs (So we can still use this table)
    "created_at": a DateTimeField automatically set to the time the record was created.
    "updated_at": a DateTimeField automatically updated with the time any changes are made to the record.
    "policy" :  a foreign key to the particular policy that the user accepted. It is set to be removed when the policy is deleted
    This model establishes a relationship between the user and the policies they have agreed to, allowing you to track which policies each user has accepted and when they did so.
    """

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_policies",
    )
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    last_notified = models.JSONField(null=True, blank=True)
    type = models.CharField(
        default=PolicyConstants.mou(),
        max_length=TINY_STR_LEN,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def simple_json(self):
        res = model_to_dict(self, ["signed_at", "id"])
        if self.policy:
            res["policy"] = self.policy.simple_json()
        return res

    def full_json(self):
        return self.simple_json()

    def __str__(self) -> str:
        if self.policy and self.signed_at:
            return f"{self.user.full_name} signed - {self.policy.name or '...'} at {self.signed_at}"
        return f"{self.user.full_name} has not yet signed policy"

    class Meta:
        ordering = ("-id",)

    class TranslationMeta:
        fields_to_translate = []


class UserMediaUpload(models.Model):
    """A class that creates a relationship between a user(all user kinds) on the platform and media they have uploaded

    Attributes
    ----------
    user : UserProfile
    A user profile object of the currently signed in user who uploaded the media

    communities: Community
    All communities that have access to the attached media object

    media : Media
    A reference to the actual media object

    is_universal: bool
    True/False value that indicates whether or not an image is open to everyone.
    PS: Its no longer being used (as at 12/10/23). We want more than two states, so we now use "publicity"

    publicity: str
    This value is used to determine whether or not an upload is OPEN_TO specific communities, CLOSED_TO, or wide open  to any communities check UserMediaConstants for all the available options

    info: JSON
    Json field that stores very important information about the attached media. Example: has_copyright_permission,copyright_att,guardian_info,size etc.

    settings: JSON
    Just another field to store more information about the media (I dont think we use this...)
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        UserProfile,
        null=True,
        related_name="uploads",
        on_delete=models.DO_NOTHING,
    )
    communities = models.ManyToManyField(
        Community,
        related_name="community_uploads",
    )
    media = models.OneToOneField(
        Media,
        null=True,
        related_name="user_upload",
        on_delete=models.CASCADE,
    )
    is_universal = BooleanField(
        default=False
    )  # True value here means image is available to EVERYONE, and EVERY COMMUNITY
    settings = models.JSONField(null=True, blank=True)
    info = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publicity = models.CharField(
        max_length=SHORT_STR_LEN,
        default=UserMediaConstants.open_to(),
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.user:
            return f"{str(self.id)} - {self.media.name} from {self.user.preferred_name or self.user.full_name} "

        return f"{str(self.id)} - {self.media.name} from ..."

    def simple_json(self):
        res = model_to_dict(
            self, ["settings", "media", "created_at", "id", "is_universal", "info", "publicity"]
        )
        res["user"] = get_summary_info(self.user)
        res["image"] = get_json_if_not_none(self.media)
        res["communities"] = [get_summary_info(com) for com in self.communities.all()]
        return res

    def full_json(self):
        return self.simple_json()

    class TranslationMeta:
        fields_to_translate = []


class DeviceProfile(models.Model):
    """
    A class used to represent a MassEnergize User's Device

    Attributes
    ----------
    user_profiles : JSON
      A JSON object containing all user ids (as foreign keys) for any users
      associated with this device.
    IP_address: Char
      The associated IP address with this device.
    device_type: Char
      The type of device we see from the HTTP request.
    operating_system:
      The operating system we see from the HTTP request.
    browser:
      The browser we see from the HTTP request.
    visit_log:
      A JSON object containing a history of dates. Activity will only be
      logged here if there is a user attached to the device and they are
      logged in.

    has_accepted_cookies:
      Boolean indicating whether or not the user has accepted cookies on this device.


    #TODO:
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    user_profiles = models.ManyToManyField(UserProfile, blank=True)
    ip_address = models.CharField(max_length=SHORT_STR_LEN, null=True)
    communities = models.ManyToManyField(Community, blank=True)
    location = models.ManyToManyField(Location, blank=True)
    device_type = models.CharField(max_length=SHORT_STR_LEN, null=True)
    operating_system = models.CharField(max_length=SHORT_STR_LEN, null=True)
    browser = models.CharField(max_length=SHORT_STR_LEN, null=True)
    visit_log = models.JSONField(default=list, null=True, blank=True)
    has_accepted_cookies = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def get_user_profiles(self):
        return json.load(self.user_profiles)

    def get_visit_log(self):
        return json.load(self.visit_log)

    def update_device_location(self, location):
        self.location.add(location)

    def update_user_profiles(self, user):
        self.user_profiles.add(user)

    def update_communities(self, community):
        self.communities.add(community)

    def update_visit_log(self, date_time):
        try:
            new_format = "%Y/%m/%d"
            date = date_time.strftime(new_format)

            # We adapt the old fomat to the new one
            if type(self.visit_log) == dict:
                old = self.visit_log
                new = []
                for day in old.keys():
                    old_format = "%d/%m/%Y"
                    if len(day) < 10:
                        old_format = "%d/%m/%y"
                    dt_object = datetime.datetime.strptime(day, old_format)
                    day = dt_object.strftime(new_format)
                    new.append(day)
                self.visit_log = new

            if type(self.visit_log) == list:
                if len(self.visit_log) > 0:
                    if date != self.visit_log[-1]:
                        self.visit_log.append(date)
                else:
                    self.visit_log.append(date)

        except Exception as e:
            print(e)
            return None, e

    def simple_json(self):
        res = model_to_dict(
            self,
            [
                "id",
                "ip_address",
                "device_type",
                "operating_system",
                "browser",
                "visit_log",
                "is_deleted",
                "has_accepted_cookies",
            ],
        )
        res["user_profiles"] = [u.simple_json() for u in self.user_profiles.all()]
        return res

    def full_json(self):
        return self.simple_json()

    class TranslationMeta:
        fields_to_translate = []


class CommunityMember(models.Model):
    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_admin = models.BooleanField(blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.user} is {'an ADMIN' if self.is_admin else 'a MEMBER'} in Community({self.community})"

    def simple_json(self):
        res = model_to_dict(self, ["id", "is_admin"])
        res["community"] = get_summary_info(self.community)
        res["user"] = get_summary_info(self.user)
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "community_members_and_admins"
        unique_together = [["community", "user"]]
        ordering = ("-created_at",)

    class TranslationMeta:
        fields_to_translate = []


class Subdomain(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        null=True,
        related_name="subdomain_community",
    )
    in_use = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.community} - {self.name}"

    def simple_json(self):
        res = model_to_dict(self, ["id", "in_use", "name", "created_at", "updated_at"])
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "subdomains"

    class TranslationMeta:
        fields_to_translate = []


class CustomCommunityWebsiteDomain(models.Model):
    id = models.AutoField(primary_key=True)
    website = models.URLField(max_length=SHORT_STR_LEN, unique=True)
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        null=True,
        related_name="community_website",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.website}-{self.community}"

    def simple_json(self):
        res = model_to_dict(self, ["id", "website", "created_at", "updated_at"])
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "custom_community_website_domain"

    class TranslationMeta:
        fields_to_translate = []


class Team(models.Model):
    """
    A class used to represent a Team in a community

    Attributes
    ----------
    name : str
      name of the team.  Need not be unique
    description: str
      description of this team
    admins: ManyToMany
      administrators for this team
    members: ManyToMany
      the team members
    community:
      which community this team is a part of
    logo:
      Foreign Key to Media file represtenting the logo for this team
    banner:
      Foreign Key to Media file represtenting the banner for this team
    created_at: DateTime
      The date and time that this goal was added
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this goal
    """

    id = models.AutoField(primary_key=True)
    # Team names should be unique globally (Not!)
    name = models.CharField(max_length=SHORT_STR_LEN)
    tagline = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)

    admins = models.ManyToManyField(UserProfile, related_name="team_admins", blank=True)
    # not used
    members = models.ManyToManyField(
        UserProfile, related_name="team_members", blank=True
    )

    # change this from ForeignKey to ManyToManyField to allow team to span communities
    # rename community to primary_community - this is the one whose cadmin can add/delete other communities, and which is unique with name
    communities = models.ManyToManyField(
        Community, related_name="community_teams", blank=True
    )
    primary_community = models.ForeignKey(
        Community, related_name="primary_community_teams", on_delete=models.CASCADE
    )
    images = models.ManyToManyField(
        Media, related_name="teams", blank=True
    )  # 0 or more photos - could be a slide show
    video_link = models.CharField(
        max_length=LONG_STR_LEN, blank=True
    )  # allow one video
    is_closed = models.BooleanField(
        default=False, blank=True
    )  # by default, teams are open
    team_page_options = models.JSONField(
        blank=True, null=True
    )  # settable team page options
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )  # for the case of sub-teams

    goal = models.ForeignKey(Goal, blank=True, null=True, on_delete=models.SET_NULL)
    logo = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_logo",
    )
    banner = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_banner",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)
    # which user created this Teamt - may be the responsible party
    user = models.ForeignKey(
        UserProfile, related_name="team_user", on_delete=models.SET_NULL, null=True, blank=True
    )

    def is_admin(self, UserProfile):
        return self.admins.filter(id=UserProfile.id)

    # def is_member(self, UserProfile):
    #  return self.members.filter(id=UserProfile.id)

    def __str__(self):
        return self.name

    def info(self):
        return model_to_dict(self, ["id", "name", "tagline", "description"])

    def simple_json(self):
        res = self.info()
        res["primary_community"] = get_json_if_not_none(self.primary_community)
        res["logo"] = get_json_if_not_none(self.logo)
        res["is_closed"] = self.is_closed
        res["is_published"] = self.is_published
        res["parent"] = get_json_if_not_none(self.parent)
        res["admins"] = [
            a.simple_json() for a in self.teammember_set.all() if a.is_admin
        ]
        return res

    def full_json(self):
        data = self.simple_json()
        # Q: should this be in simple_json?
        data["communities"] = [c.simple_json() for c in self.communities.all()]
        data["members"] = [m.info() for m in self.members.all()]
        data["goal"] = get_json_if_not_none(self.goal)
        data["banner"] = get_json_if_not_none(self.banner)
        return data

    class Meta:
        ordering = ("name",)
        db_table = "teams"
        unique_together = [["primary_community", "name"]]

    class TranslationMeta:
        fields_to_translate = ["name", "tagline", "description"]


class TeamMember(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_admin = models.BooleanField(blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.user} is {'an ADMIN' if self.is_admin else 'a MEMBER'} in Team({self.team})"

    def simple_json(self):
        res = model_to_dict(self, ["id", "is_admin"])
        res["team"] = get_summary_info(self.team)
        res["user"] = get_summary_info(self.user)
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "team_members_and_admins"
        unique_together = [["team", "user"]]

    class TranslationMeta:
        fields_to_translate = []


class Service(models.Model):
    """
    A class used to represent a Service provided by a Vendor

    Attributes
    ----------
    name : str
      name of the service
    description: str
      description of this service
    image: int
      Foreign Key to a Media file represtenting an image for this service if any
    icon: str
      a string description of an icon class for this service if any
    info: JSON
      any another dynamic information we would like to store about this Service
    created_at: DateTime
      The date and time that this goal was added
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this goal
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
    description = models.CharField(max_length=LONG_STR_LEN, blank=True)
    service_location = models.JSONField(blank=True, null=True)
    image = models.ForeignKey(Media, blank=True, null=True, on_delete=models.SET_NULL)
    icon = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        return model_to_dict(
            self, ["id", "name", "description", "service_location", "icon"]
        )

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "services"

    class TranslationMeta:
        fields_to_translate = ["description", "name"]


class ActionProperty(models.Model):
    """
    A class used to represent an Action property.

    Attributes
    ----------
    name : str
      name of the Vendor
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
    short_description = models.CharField(max_length=LONG_STR_LEN, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.full_json()

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ("id",)
        db_table = "action_properties"

    class TranslationMeta:
        fields_to_translate = ["name", "short_description"]


class CarbonEquivalency(models.Model):
    """
    Represents an carbon equivalency that can make
    carbon impact more comprehensible to users.

    Attributes
    ----------
    name : str
      Name of the unit used. E.g. "Tree"
    value: int
      Value is how many pounds per year of CO2 per unit of this.  Use https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator
    icon:
      Graphic representing the appropriate equivalancey.
    explanation: str
      Additional information on the equivelancy. E.g.
      "A typical hardwood tree can absorb as much as 48
      pounds of carbon dioxide per year"
    reference: str
      Source of information used. Link, book, study, etc.
    date: DateTime
      Timestamp of when the equivilancy was last modified.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    value = models.FloatField()
    icon = models.CharField(max_length=50)
    title = models.CharField(max_length=40, null=True, blank=True)
    explanation = models.CharField(max_length=100)
    reference = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class Meta:
        verbose_name_plural = "CarbonEquivalencies"
        ordering = ("id",)
        db_table = "carbon_equivalencies"

    class TranslationMeta:
        fields_to_translate = ["name", "explanation"]


class Vendor(models.Model):
    """
    A class used to represent a Vendor/Contractor that provides a service
    associated with any of the actions.

    Attributes
    ----------
    name : str
      name of the Vendor
    description: str
      description of this service
    logo: int
      Foreign Key to Media file represtenting the logo for this Vendor
    banner: int
      Foreign Key to Media file represtenting the banner for this Vendor
    address: int
      Foreign Key for Location of this Vendor
    key_contact: int
      Foreign Key for MassEnergize User that is the key contact for this vendor
    service_area: str
      Information about whether this vendor provides services nationally,
      statewide, county or Town services only
    properties_services: str
      Whether this vendor services Residential or Commercial units only
    onboarding_date: DateTime
      When this vendor was onboard-ed on the MassEnergize Platform for this
        community
    onboarding_contact:
      Which MassEnergize Staff/User onboard-ed this vendor
    verification_checklist:
      contains information about some steps and checks needed for due diligence
      to be done on this vendor eg. Vendor MOU, Reesearch
    is_verified: boolean
      When the checklist items are all done and verified then set this as True
      to confirm this vendor
    more_info: JSON
      any another dynamic information we would like to store about this Service
    created_at: DateTime
      The date and time that this Vendor was added
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this Vendor
    is_approved: boolean
      after the community admin reviews this, can check the box

    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
    phone_number = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    email = models.EmailField(blank=True, null=True, db_index=True)
    description = models.CharField(max_length=LONG_STR_LEN, blank=True)
    logo = models.ForeignKey(
        Media,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="vender_logo",
    )
    banner = models.ForeignKey(
        Media,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="vendor_banner",
    )
    address = models.JSONField(blank=True, null=True)
    key_contact = models.JSONField(blank=True, null=True)
    service_area = models.CharField(max_length=SHORT_STR_LEN)
    service_area_states = models.JSONField(blank=True, null=True)
    services = models.ManyToManyField(Service, blank=True)
    properties_serviced = models.JSONField(blank=True, null=True)
    onboarding_date = models.DateTimeField(auto_now_add=True)
    onboarding_contact = models.ForeignKey(
        UserProfile,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="onboarding_contact",
    )
    verification_checklist = models.JSONField(blank=True, null=True)
    is_verified = models.BooleanField(default=False, blank=True)
    location = models.JSONField(blank=True, null=True)
    more_info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    communities = models.ManyToManyField(
        Community, blank=True, related_name="community_vendors"
    )
    tags = models.ManyToManyField(Tag, related_name="vendor_tags", blank=True)
    # which user posted this vendor
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)
    is_approved = models.BooleanField(default=False, blank=True)
    # is_user_submitted = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.name

    def info(self):
        data = model_to_dict(
            self, ["id", "name", "service_area", "key_contact", "phone_number", "email"]
        )
        data["logo"] = get_json_if_not_none(self.logo)
        return data

    def get_field_from_more_info(self, key):
        if self.more_info:
            if isinstance(self.more_info, str):
                self.more_info = json.loads(self.more_info)
            return self.more_info.get(key, None)
        return None

    def simple_json(self):
        data = model_to_dict(
            self,
            exclude=[
                "logo",
                "banner",
                "services",
                "onboarding_contact",
                "more_info",
                "services",
                "communities",
            ],
        )
        data["services"] = [s.simple_json() for s in self.services.all()]
        data["communities"] = [c.simple_json() for c in self.communities.all()]
        data["tags"] = [t.simple_json() for t in self.tags.all()]
        data["logo"] = get_json_if_not_none(self.logo)
        data["website"] = self.get_field_from_more_info("website")
        data["key_contact"] = self.key_contact
        return data

    def full_json(self):
        data = model_to_dict(
            self, exclude=["logo", "banner", "services", "onboarding_contact"]
        )
        data["onboarding_contact"] = get_json_if_not_none(self.onboarding_contact)
        data["logo"] = get_json_if_not_none(self.logo)
        data["more_info"] = self.more_info
        data["tags"] = [t.simple_json() for t in self.tags.all()]
        data["banner"] = get_json_if_not_none(self.banner)
        data["services"] = [s.simple_json() for s in self.services.all()]
        data["communities"] = [c.simple_json() for c in self.communities.all()]
        data["website"] = self.get_field_from_more_info("website")
        data["key_contact"] = self.key_contact
        data["location"] = self.location
        if self.user:
            data["user_email"] = self.user.email

        return data

    class Meta:
        db_table = "vendors"

    class TranslationMeta:
        fields_to_translate = ["description", "name"]


class Action(models.Model):
    """
    A class used to represent an Action that can be taken by a user on this
    website.

    Attributes
    ----------
    title : str
      A short title for this Action.
    is_global: boolean
      True if this action is a core action that every community should see or not.
      False otherwise.
    about: str
      More descriptive information about this action.
    steps_to_take: str
      Describes the steps that can be taken by an a user for this action;
    icon: str
      a string description of the icon class for this action if any
    image: int Media
      a Foreign key to an uploaded media file
    average_carbon_score:
      the average carbon score for this action as given by the carbon calculator
    geographic_area: str
      the Location where this action can be taken
    created_at: DateTime
      The date and time that this real estate unity was added
    created_at: DateTime
      The date and time of the last time any updates were made to the information
      about this real estate unit
    is_approved: boolean
      after the community admin reviews this, can check the box

    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=SHORT_STR_LEN, db_index=True)
    is_global = models.BooleanField(default=False, blank=True)
    featured_summary = models.TextField(max_length=LONG_STR_LEN, blank=True, null=True)
    steps_to_take = models.TextField(max_length=LONG_STR_LEN, blank=True)
    deep_dive = models.TextField(max_length=LONG_STR_LEN, blank=True)
    about = models.TextField(max_length=LONG_STR_LEN, blank=True)
    # TODO: this wasn't fully implemented - may remove primary_category
    # this is the singal category which points will be recorded in, though
    primary_category = models.ForeignKey(
        Tag, related_name="action_category", on_delete=models.SET_NULL, null=True
    )
    # then - an action could have multiple secondary categories
    tags = models.ManyToManyField(Tag, related_name="action_tags", blank=True)
    geographic_area = models.JSONField(blank=True, null=True)
    icon = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    image = models.ForeignKey(
        Media, on_delete=models.SET_NULL, null=True, blank=True, related_name="actions"
    )
    properties = models.ManyToManyField(ActionProperty, blank=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    calculator_action = models.ForeignKey(
        CCAction, blank=True, null=True, on_delete=models.SET_NULL
    )
    average_carbon_score = models.TextField(max_length=SHORT_STR_LEN, blank=True)
    community = models.ForeignKey(
        Community, on_delete=models.SET_NULL, null=True, blank=True, db_index=True
    )
    rank = models.PositiveSmallIntegerField(default=0, blank=True)
    # which user posted this action originally
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)
    is_approved = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{str(self.id)} - {self.title}"

    def info(self):
        return {
            **model_to_dict(self, ["id", "title"]),
            "community":{
                "id": self.community.id,
                "name": self.community.name,
            }
        }

    def simple_json(self):
        data = model_to_dict(
            self,
            [
                "id",
                "is_published",
                "is_approved",
                "is_deleted",
                "title",
                "is_global",
                "icon",
                "rank",
                "average_carbon_score",
                "featured_summary",
                "steps_to_take",
                "deep_dive",
                "about",
                # "is_user_submitted",
            ],
        )
        data["image"] = get_summary_info(self.image)
        data["calculator_action"] = get_summary_info(self.calculator_action)
        if self.calculator_action:
            data["category"] =  self.calculator_action.category.simple_json() if self.calculator_action.category else None
            data["subcategory"] = self.calculator_action.sub_category.simple_json() if self.calculator_action.sub_category else None
        data["tags"] = [t.simple_json() for t in self.tags.all()]
        data["community"] = get_summary_info(self.community)
        data["created_at"] = self.created_at
        data["updated_at"] = self.updated_at
        # Adding this so that vendors will be preselected when creating/updating action.
        # List of vendors will typically not be that long, so this doesnt pose any problems
        data["vendors"] = [v.info() for v in self.vendors.all()]
        data["action_users"] = (
            len(UserActionRel.objects.filter(action=self, is_deleted=False)) or 0
        )

        if self.user:
            data["user_email"] = self.user.email
        return data

    def full_json(self):
        data = self.simple_json()
        data["is_global"] = self.is_global
        # data["steps_to_take"] = self.steps_to_take
        # data["about"] = self.about
        data["geographic_area"] = self.geographic_area
        data["properties"] = [p.simple_json() for p in self.properties.all()]
        data["action_users"] = [
            {
                "id": u.id,
                "status": u.status,
                "email": u.user.email,
                "full_name": u.user.full_name,
                "real_estate_unit": {
                    "zipcode": u.real_estate_unit.address.zipcode
                    if u.real_estate_unit and u.real_estate_unit.address
                    else None,
                    "name": u.real_estate_unit.name if u.real_estate_unit else None,
                },
                "date_completed": u.date_completed,
                "carbon_impact": AverageImpact(u.action.calculator_action, u.date_completed) if u.action.calculator_action else None,
                "recorded_at": u.updated_at,
            }
            for u in UserActionRel.objects.filter(action=self, is_deleted=False)
        ] or []
        # data["vendors"] = [v.simple_json() for v in self.vendors.all()]
        if self.user:
            data["user_email"] = self.user.email
        return data

    class Meta:
        ordering = ["rank", "title"]
        db_table = "actions"

    class TranslationMeta:
        fields_to_translate = ["title", "about", "steps_to_take", "deep_dive", "featured_summary"]


class Event(models.Model):
    """
    A class used to represent an Event.

    Attributes
    ----------
    name : str
      name of the event
    description: str
      more details about this event
    start_date_and_time: Datetime
      when the event starts (both the day and time)
    end_date_and_time: Datetime
      when the event ends
    location: Location
      where the event is taking place
    tags: ManyToMany
      tags on this event to help in easily filtering
    image: Media
      Foreign key linking to the image attached to this event.
    archive: boolean
      True if this event should be archived
    is_global: boolean
      True if this action is an event that every community should see or not.
      False otherwise.
    is_recurring: boolean
      if the event is recurring, this value is True
      and it has a RecurringPattern instance attached to it.
    recurring_details: JSON
      stores information about the recurrence pattern of the event if is_recurring = True
    is_approved: boolean
      after the community admin reviews this, can check the box

    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    featured_summary = models.TextField(max_length=LONG_STR_LEN, blank=True, null=True)
    description = models.TextField(max_length=LONG_STR_LEN)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True)
    invited_communities = models.ManyToManyField(
        Community, related_name="invited_communites", blank=True
    )
    start_date_and_time = models.DateTimeField(db_index=True)
    end_date_and_time = models.DateTimeField(db_index=True)
    location = models.JSONField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    archive = models.BooleanField(default=False, blank=True)
    is_global = models.BooleanField(default=False, blank=True)
    external_link = models.CharField(max_length=LONG_STR_LEN, blank=True, null=True)
    rsvp_enabled = models.BooleanField(default=False, blank=True)
    rsvp_email = models.BooleanField(default=False, blank=True)
    rsvp_message = models.TextField(max_length=LONG_STR_LEN, blank=True)
    more_info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)
    rank = models.PositiveIntegerField(default=0, blank=True, null=True)
    # which user posted this event - may be the responsible party
    user = models.ForeignKey(UserProfile, related_name="event_user", on_delete=models.SET_NULL, null=True, blank=True)
    is_recurring = models.BooleanField(default=False, blank=True, null=True)
    recurring_details = models.JSONField(blank=True, null=True)
    is_approved = models.BooleanField(default=False, blank=True)
    # Made publicity a string, so we can handle more than two (open/close) states
    publicity = models.CharField(max_length=SHORT_STR_LEN, default=EventConstants.open())
    # If any community is added here, it means the event is either (Open to / Closed to) depending
    # on what the value of "publicity" is
    communities_under_publicity = models.ManyToManyField(Community, related_name="event_access_selections", blank=True)
    # Communities that have shared an event to their site will be in this list
    shared_to = models.ManyToManyField(Community, related_name="events_from_others", blank=True)
    # Date and time when the event went live
    published_at = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    external_link_type = models.CharField(max_length=SHORT_STR_LEN, blank=True)

    def __str__(self):
        return self.name

    def info(self):
        data = model_to_dict(self, ["id", "name"])
        return data
    def communities_shared_to(self):
        communities = self.communities_under_publicity.all()
        if self.publicity == EventConstants.open_to():
            return communities
        elif self.publicity == EventConstants.closed_to():
            communities_ids = communities.values_list('id', flat=True)
            return Community.objects.exclude(id__in=communities_ids)
        return []

    def is_on_homepage(self) -> bool:
        is_used = False
        home_page = HomePageSettings.objects.filter(community=self.community).first()
        if home_page and home_page.featured_events:
            is_used = home_page.featured_events.filter(id=self.id, start_date_and_time__gte=timezone.now()).exists()
        return is_used

    def simple_json(self):
        data = model_to_dict(
            self,
            exclude=[
                "tags",
                "image",
                "community",
                "invited_communities",
                "user",
                "communities_under_publicity",
                "shared_to",
            ],
        )
        data["tags"] = [t.info() for t in self.tags.all()]
        data["community"] = None if not self.community else self.community.info()
        data["image"] = None if not self.image else self.image.info()
        #data["invited_communities"] = [ c.info() for c in self.invited_communities.all()]
        data["is_open"] =  False if not self.publicity else EventConstants.is_open(self.publicity)
        data["is_open_to"] = False if not self.publicity else EventConstants.is_open_to(self.publicity)
        data["is_closed_to"] = False if not self.publicity else EventConstants.is_closed_to(self.publicity)
        data["communities_under_publicity"] = [c.info() for c in self.communities_under_publicity.all()]

        if self.user:
            data["user_email"] = self.user.email

        data["shared_to"] = [c.info() for c in self.shared_to.all()]
        data["is_on_home_page"] = self.is_on_homepage()

        data["event_type"] = self.event_type if self.event_type else "Online" if not self.location else "In-Person"
        data["settings"] = dict(notifications=[x.simple_json() for x in self.nudge_settings.all().order_by("-created_at") if x.communities.exists()])

        return data

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = (
            "rank",
            "-start_date_and_time",
        )
        db_table = "events"

    class TranslationMeta:
        fields_to_translate = ["name", "description", "featured_summary", "rsvp_message", "external_link_type", "event_type"]


class EventNudgeSetting(models.Model):
    """
    A class used to represent the settings for nudges for an event.
    Communities: the list of communities this setting apply to for the event
    settings: the settings for the event. sample:{'when_first_posted': False,'within_30_days': True,'within_1_week': False, 'never': False}
    creator: the user who created this setting
    more_info: any other information about this settings
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="nudge_settings")
    communities = models.ManyToManyField(Community, related_name="nudge_settings_communities", blank=True)

    when_first_posted = models.BooleanField(default=False, blank=True)
    within_30_days = models.BooleanField(default=True, blank=True)
    within_1_week = models.BooleanField(default=True, blank=True)
    never = models.BooleanField(default=False, blank=True)
    last_updated_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name="nudge_settings_last_updated_by", blank=True)
    creator = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name="nudge_settings_creator", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.name} - {str(self.id)}"

    def simple_json(self):
        data = model_to_dict(self, exclude=["event", "communities", "last_updated_by", "creator"])
        data["id"] =str(self.id)
        data["communities"] = [c.simple_json() for c in self.communities.all()]
        data["settings"] = {
            "when_first_posted": self.when_first_posted,
            "within_30_days": self.within_30_days,
            "within_1_week": self.within_1_week,
            "never": self.never,
        }
        return data

    def full_json(self):
        res = self.simple_json()
        res["event"] = self.event.info()
        return res

    class TranslationMeta:
        fields_to_translate = []



# leaner class that stores information about events that have already passed
# in the future, can use this class to revive events that may have been archived
class PastEvent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    description = models.TextField(max_length=LONG_STR_LEN)
    start_date_and_time = models.DateTimeField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    class TranslationMeta:
        fields_to_translate = []


class RecurringEventException(models.Model):
    """
    A class used to represent a RESCHEDULING of a recurring event.

    Attributes
    ----------
    event: Event
      stores the recurring event that the exception is attached to
    rescheduled_event: Event
      if the event instance is rescheduled, a new Event is created
      representing the rescheduled event instance
    is_cancelled : boolean
      True if the event has been cancelled by CAdmin
    is_rescheduled: boolean
      True if event has been rescheduled by CAdmin
    former_time: dateTime
      Tells us when the instance was originally scheduled. Helps us figure out when to delete RecurringEventException
    """

    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="recurring_event"
    )
    rescheduled_event = models.ForeignKey(
        Event, on_delete=models.CASCADE, blank=True, null=True
    )
    # shouldnt be this way - blank should be false, but I don't know what to set the default to
    former_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def simple_json(self):
        data = model_to_dict(self, exclude=["event", "rescheduled_event"])
        data["id"] = str(self.id)
        data["former_time"] = str(self.former_time)
        data["event"] = self.event.id
        data["rescheduled_start_time"] = str(self.rescheduled_event.start_date_and_time)
        data["rescheduled_end_time"] = str(self.rescheduled_event.end_date_and_time)
        return data

    class TranslationMeta:
        fields_to_translate = []


class EventAttendee(models.Model):
    """
    A class used to represent events and attendees

    Attributes
    ----------
    user : Foreign Key of the User
      Which user this applies to
    status: str
      Tells if the user is just interested, RSVP-ed or saved for later.
    event: int
      Foreign Key to event that the user has responded to.
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=TINY_STR_LEN, choices=CHOICES.get("EVENT_CHOICES", {}).items()
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "%s | %s | %s" % (self.user, self.status, self.event)

    def simple_json(self):
        data = model_to_dict(self, ["id", "status"])
        data["user"] = self.user.info()
        data["event"] = self.event.info()
        return data

    def full_json(self):
        return self.simple_json()

    class Meta:
        verbose_name_plural = "Event Attendees"
        db_table = "event_attendees"
        unique_together = [["user", "event"]]

    class TranslationMeta:
        fields_to_translate = []


class Permission(models.Model):
    """
     A class used to represent Permission(s) that are required by users to perform
     any tasks on this platform.


    Attributes
    ----------
    name : str
      name of the Vendor
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=TINY_STR_LEN,
        choices=CHOICES.get("PERMISSION_TYPES", {}).items(),
        db_index=True,
    )
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return CHOICES.get("PERMISSION_TYPES", {})[self.name]

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ("name",)
        db_table = "permissions"

    class TranslationMeta:
        fields_to_translate = ["description", "name"]


class UserPermissions(models.Model):
    """
    A class used to represent Users and what they can do.

    Attributes
    ----------
    who : int
      the user on this site
    can_do: int
      Foreign Key desscribing the policy that they can perform
    """

    id = models.AutoField(primary_key=True)
    who = models.ForeignKey(Role, on_delete=models.CASCADE)
    can_do = models.ForeignKey(Permission, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "(%s) can (%s)" % (self.who, self.can_do)

    def simple_json(self):
        return {
            "id": self.id,
            "who": get_json_if_not_none(self.who),
            "can_do": get_json_if_not_none(self.can_do),
        }

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ("who",)
        db_table = "user_permissions"

    class TranslationMeta:
        fields_to_translate = []


class Testimonial(models.Model):
    """
     A class used to represent a Testimonial shared by a user.


    Attributes
    ----------
    title : str
      title of the testimony
    body: str (HTML)
      more information for this testimony.
    is_approved: boolean
      after the community admin reviews this, can check the box
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=SHORT_STR_LEN, db_index=True)
    body = models.TextField(max_length=LONG_STR_LEN)
    is_approved = models.BooleanField(default=False, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="testimonials",
    )
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, db_index=True, null=True
    )
    action = models.ForeignKey(
        Action, on_delete=models.CASCADE, null=True, db_index=True
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL, null=True, blank=True, db_index=True
    )
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, blank=True, null=True, db_index=True
    )
    rank = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)
    anonymous = models.BooleanField(default=False, blank=True)
    preferred_name = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    other_vendor = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    more_info = models.JSONField(blank=True, null=True)
    # is_user_submitted = models.BooleanField(default=False, blank=True, null=True)
    sharing_type = models.CharField( max_length=SHORT_STR_LEN, choices=SharingType.choices(), default=SharingType.OPEN.value[0])
    shared_with = models.ManyToManyField(Community, related_name="shared_testimonials", blank=True)

    def __str__(self):
        return self.title

    def info(self):
        return model_to_dict(self, fields=["id", "title", "community"])

    def _get_user_info(self):
        return get_json_if_not_none(self.user) or {
            "full_name": "User unknown",
            "email": "e-mail address not provided",
        }

    def simple_json(self):
        res = model_to_dict(self, exclude=["image", "tags"])
        res["user"] = None if not self.user else self.user.info()
        res["action"] = None if not self.action else self.action.info()
        res["vendor"] = None if not self.vendor else self.vendor.info()
        res["community"] = None if not self.community else self.community.info()
        res["created_at"] = self.created_at.date()
        res["file"] = None if not self.image else self.image.info()
        res["tags"] = [t.simple_json() for t in self.tags.all()]
        res["anonymous"] = self.anonymous
        res["preferred_name"] = self.preferred_name
        res["other_vendor"] = self.other_vendor
        return res

    def full_json(self):
        data = self.simple_json()
        data["image"] = data.get("file", None)
        data["tags"] = [t.simple_json() for t in self.tags.all()]
        return data

    class Meta:
        ordering = ("rank",)
        db_table = "testimonials"

    class TranslationMeta:
        fields_to_translate = ["title", "body"]


class UserActionRel(models.Model):
    """
     A class used to represent a user and his/her relationship with an action.
     Whether they marked an action as todo, done, etc


    Attributes
    ----------
    user : int
      Foreign Key for user
    real_estate_unit:
      Foreign key for the real estate unit this action is related to.
    action: int
      which action they marked
    vendor:
      which vendor they choose to contact/connect with
    status:
      Whether they marked it as todo, done or save for later
    date_completed:
      If specified, the date when they completed the action
    carbon_impact:
      Carbon reduction calculated by the Carbon Calculator
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_index=True)
    real_estate_unit = models.ForeignKey(RealEstateUnit, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=SHORT_STR_LEN,
        choices=CHOICES.get("USER_ACTION_STATUS", {}).items(),
        db_index=True,
        default="TODO",
    )
    date_completed = models.DateField(blank=True, null=True)
    carbon_impact = models.IntegerField(
        default=0
    )  # that which was calculated by the Carbon Calculator
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def simple_json(self):
        return {
            "id": self.id,
            "user": get_json_if_not_none(self.user),
            "action": get_json_if_not_none(self.action),
            "real_estate_unit": get_json_if_not_none(self.real_estate_unit),
            "status": self.status,
            "date_completed": self.date_completed,
            "carbon_impact": self.carbon_impact,
        }

    def full_json(self):
        res = self.simple_json()
        res["vendor"] = get_json_if_not_none(self.vendor)
        return res

    def __str__(self):
        return "%s - %s | %s | (%s)" % (
            str(self.id),
            self.user,
            self.status,
            self.action,
        )

    class Meta:
        ordering = ("-id", "status", "user", "action")
        unique_together = [["user", "action", "real_estate_unit"]]

    class TranslationMeta:
        fields_to_translate = []


class CommunityAdminGroup(models.Model):
    """
    This represents a binding of a group of users and a community for which they
    are admin for.

    Attributes
    ----------
    name : str
      name of the page section
    info: JSON
      dynamic information goes in here
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True, db_index=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, blank=True)
    members = models.ManyToManyField(UserProfile, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    pending_admins = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + " " + self.name

    def simple_json(self):
        res = model_to_dict(self, exclude=["members"])
        res["community"] = get_json_if_not_none(self.community)
        res["members"] = [m.info() for m in self.members.all()]
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ["-id"]
        db_table = "community_admin_group"

    class TranslationMeta:
        fields_to_translate = []


class UserGroup(models.Model):
    """
    This represents a binding of a group of users and a community
    and the permissions they have.

    Attributes
    ----------
    name : str
      name of the page section
    info: JSON
      dynamic information goes in here
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True, db_index=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, blank=True, db_index=True
    )
    members = models.ManyToManyField(UserProfile, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        return model_to_dict(self, exclude=["members", "permissions"])

    def full_json(self):
        data = self.simple_json()
        data["community"] = get_json_if_not_none(self.community)
        data["members"] = [m.info() for m in self.members.all()]
        data["permissions"] = [p.simple_json() for p in self.permissions.all()]
        return data

    class Meta:
        ordering = ("name",)
        db_table = "user_groups"

    class TranslationMeta:
        fields_to_translate = ["description", "name"]


class Data(models.Model):
    """Instances of data points

    Attributes
    ----------
    name : str
      name of the statistic
    value: decimal
      The value of the statistic goes here
    info: JSON
      dynamic information goes in here.  The symbol and other info goes here
    community: int
      foreign key linking a community to this statistic
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, db_index=True)
    value = models.PositiveIntegerField(default=0)
    reported_value = models.PositiveIntegerField(default=0)
    denominator = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    symbol = models.CharField(max_length=LONG_STR_LEN, blank=True)
    tag = models.ForeignKey(
        Tag, blank=True, on_delete=models.CASCADE, null=True, db_index=True
    )
    community = models.ForeignKey(
        Community, blank=True, on_delete=models.SET_NULL, null=True, db_index=True
    )
    info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return "%s | %s (%d) |(%s)" % (self.community, self.name, self.value, self.tag)

    def simple_json(self):
        return model_to_dict(self, fields=["id", "name", "value", "reported_value"])

    def full_json(self):
        data = self.simple_json()
        data["tag"] = get_json_if_not_none(self.tag)
        data["community"] = get_json_if_not_none(self.community)
        return data

    class Meta:
        verbose_name_plural = "Data"
        ordering = ("name", "value")
        db_table = "data"

    class TranslationMeta:
        fields_to_translate = []


class Graph(models.Model):
    """Instances keep track of a statistic from the admin

    Attributes
    ----------
    title : str
      the title of this graph
    type: str
      the type of graph to be plotted eg. pie chart, bar chart etc
    data: JSON
      data to be plotted on this graph
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=LONG_STR_LEN, db_index=True)
    graph_type = models.CharField(
        max_length=TINY_STR_LEN, choices=CHOICES.get("GRAPH_TYPES", {}).items()
    )
    community = models.ForeignKey(
        Community, on_delete=models.SET_NULL, null=True, blank=True
    )
    data = models.ManyToManyField(Data, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def simple_json(self):
        return model_to_dict(self, fields=["title", "community", "is_published"])

    def full_json(self):
        res = self.simple_json()
        res["data"] = [d.simple_json() for d in self.data.all()]
        return res

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Graphs"
        ordering = ("title",)

    class TranslationMeta:
        fields_to_translate = ["title"]


class Button(models.Model):
    """Buttons on the pages"""

    text = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    icon = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    url = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    color = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.text

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ("text",)


class SliderImage(models.Model):
    """Model the represents the database for Images that will be
    inserted into slide shows

    Attributes
    ----------
    title : str
      title of the page section
    subtitle: str
      sub title for this image as should appear on the slider
    buttons: JSON
      a json list of buttons with each containing text, link, icon, color etc
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=LONG_STR_LEN, blank=True, db_index=True)
    subtitle = models.CharField(max_length=LONG_STR_LEN, blank=True)
    image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True)
    buttons = models.ManyToManyField(Button, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.title

    def simple_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "image": get_json_if_not_none(self.image),
        }

    def full_json(self):
        res = self.simple_json()
        res["buttons"] = [b.simple_json() for b in self.buttons.all()]
        return res

    class Meta:
        verbose_name_plural = "Slider Images"
        db_table = "slider_images"

class Slider(models.Model):
    """
    Model that represents a model for a slider/carousel on the website

    Attributes
    ----------
    name : str
      name of the page section
    description: str
      a description of this slider
    info: JSON
      dynamic information goes in here
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=LONG_STR_LEN, blank=True, db_index=True)
    description = models.CharField(max_length=LONG_STR_LEN, blank=True)
    slides = models.ManyToManyField(SliderImage, blank=True)
    is_global = models.BooleanField(default=False, blank=True)
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    def full_json(self):
        res = self.simple_json()
        res["slides"] = [s.full_json() for s in self.slides.all()]
        return res



class Menu(models.Model):
    """Represents items on the menu/navigation bar (top-most bar on the webpage)
    Attributes
    ----------
    name : str
      name of the page section
    content: JSON
      the content is represented as a json
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=LONG_STR_LEN, unique=True)
    content = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
    community_logo_link = models.CharField(max_length=LONG_STR_LEN, blank=True, null=True)
    is_custom = models.BooleanField(default=False, blank=True)
    footer_content = models.JSONField(blank=True, null=True)
    contact_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        res =  model_to_dict(self)
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ("name",)

    class TranslationMeta:
        fields_to_translate = ["name"]


class Card(models.Model):
    """Buttons on the pages"""

    title = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    icon = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    link = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    media = models.ForeignKey(Media, blank=True, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def simple_json(self):
        return {
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "link": self.link,
            "media": get_json_if_not_none(self.media),
        }

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ("title",)


class PageSection(models.Model):
    """
     A class used to represent a PageSection
     #TODO: what about page sections like a gallery, slideshow, etc?

    Attributes
    ----------
    name : str
      name of the page section
    info: JSON
      dynamic information goes in here
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    title = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True)
    cards = models.ManyToManyField(Card, blank=True)
    buttons = models.ManyToManyField(Button, blank=True)
    slider = models.ForeignKey(Slider, on_delete=models.SET_NULL, null=True, blank=True)
    graphs = models.ManyToManyField(Graph, blank=True, related_name="graphs")
    info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        return model_to_dict(self, ["id", "name", "title", "description"])

    def full_json(self):
        res = self.simple_json()
        res["image"] = get_json_if_not_none(self.image)
        res["cards"] = [c.simple_json() for c in self.cards.all()]
        res["buttons"] = ([b.simple_json() for b in self.buttons.all()],)
        res["slider"] = (get_json_if_not_none(self.slider, True),)
        res["graphs"] = ([g.full_json() for g in self.graphs.all()],)
        res["info"] = self.info
        return res


class Page(models.Model):
    """
     A class used to represent a Page on a community portal
     eg. The home page, about-us page, etc

    Attributes
    ----------
    title : str
      title of the page
    description: str
      the description of the page
    community: int
      Foreign key for which community this page is linked to
    sections: ManyToMany
      all the different parts/sections that go on this page
    content: JSON
      dynamic info for this page goes here.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=LONG_STR_LEN, db_index=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    sections = models.ManyToManyField(PageSection, blank=True)
    info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.name} - {self.community.name}"

    def simple_json(self):
        res = model_to_dict(self, ["id", "name", "description"])
        res["community"] = get_json_if_not_none(self.community)
        return res

    def full_json(self):
        res = self.simple_json()
        res["sections"] = [s.full_json() for s in self.sections.all()]
        res["info"] = self.info
        return res

    class Meta:
        unique_together = [["name", "community"]]


class BillingStatement(models.Model):
    """
     A class used to represent a Billing Statement

    Attributes
    ----------
    name : str
      name of the statement.
    amount: decimal
      the amount of money owed
    description:
      the breakdown of the bill for this community
    community: int
      Foreign Key to the community to whom this bill is associated.
    start_date: Datetime
      the start date from which the charges were incurred
    end_date:
      the end date up to which this charge was incurred.
    more_info: JSON
      dynamic information goes in here
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    amount = models.CharField(max_length=SHORT_STR_LEN, default="0.0")
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    start_date = models.DateTimeField(blank=True, db_index=True)
    end_date = models.DateTimeField(blank=True)
    more_info = models.JSONField(blank=True, null=True)
    community = models.ForeignKey(
        Community, on_delete=models.SET_NULL, null=True, db_index=True
    )
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        res = model_to_dict(self, exclude=["community"])
        res["community"] = get_json_if_not_none(self.community)
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        ordering = ("name",)
        db_table = "billing_statements"


class Subscriber(models.Model):
    """
     A class used to represent a subscriber / someone who wants to join the
     massenergize mailist

    Attributes
    ----------
    name : str
      name of the statement.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN)
    email = models.EmailField(blank=False, db_index=True)
    community = models.ForeignKey(
        Community, on_delete=models.SET_NULL, null=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        res = model_to_dict(self)
        res["community"] = None if not self.community else self.community.info()
        res["subscribed"] = self.created_at.date()
        return res

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "subscribers"
        unique_together = [["email", "community"]]


class EmailCategory(models.Model):
    """
    A class tha represents an email preference that a user or subscriber can
    subscribe to.

    Attributes
    ----------
    name : str
      the name for this email preference
    community: int
      Foreign Key to the community this email category is associated with
    is_global: boolean
      True if this email category should appear in all the communities
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, db_index=True)
    community = models.ForeignKey(Community, db_index=True, on_delete=models.CASCADE)
    is_global = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        res = self.simple_json()
        res["community"] = get_json_if_not_none(self.community)
        return res

    class Meta:
        db_table = "email_categories"
        unique_together = [["name", "community"]]
        verbose_name_plural = "Email Categories"


class SubscriberEmailPreference(models.Model):
    """
    Represents the email preferences of each subscriber.
    For a subscriber might want marketing emails but not promotion emails etc

    Attributes
    ----------
    subscriber: int
      Foreign Key to a subscriber
    email_category: int
      Foreign key to an email category
    """

    id = models.AutoField(primary_key=True)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, db_index=True)
    subscribed_to = models.ForeignKey(EmailCategory, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "%s - %s" % (self.subscriber, self.subscribed_to)

    def simple_json(self):
        return {
            "id": self.id,
            "subscriber": get_json_if_not_none(self.subscriber),
            "subscribed_to": get_json_if_not_none(self.subscribed_to),
        }

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "subscriber_email_preferences"


class PageSettings(models.Model):
    """
    Represents the basic page settings.  This is a base class, which contains common attributes to most page settings.

    Attributes
    ----------
    Community:
      Foreign key: Which community this applies to
    title: str
      Title of the page (if different than default)
    sub_title: str
      Sub-title or tag-line of the page (if different than default)
    description: str
      Description of the page (if different than default)
    images:
      ForeignKeys: Links to one or more Media records
    featured_video_link: str
      A link to a featured video (on YouTube or elsewhere)
    more_info: JSON - extraneous information
    is_deleted: boolean - whether this page was deleted from the platform (perhaps with it's community)
    is_published: boolean - whether this page is live
    is_template: boolean - whether this is a template to be copied
    """

    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    images = models.ManyToManyField(Media, blank=True)
    featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    more_info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def simple_json(self):
        res = model_to_dict(self, exclude=["images"])
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        res = self.simple_json()
        res["images"] = [i.simple_json() for i in self.images.all()]
        return res

    class Meta:
        abstract = True


class ImageSequence(models.Model):
    """
    A class used to record the arrangement of images, wherever there is a need.
    """

    name = models.CharField(max_length=SHORT_STR_LEN)
    sequence = models.JSONField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name or super().__str__()


class HomePageSettings(models.Model):
    """
    Represents the community's Home page settings.

    Attributes
    ----------
    Community:
      Foreign key: Which community this applies to
    title: str
      Title of the page (if different than default)
    sub_title: str
      Sub-title or tag-line of the page (if different than default)
    description: str
      Description of the page (if different than default)
    images:
      ForeignKeys: Links to one or more Media records
    featured_video_link: str
      A link to a featured video (on YouTube or elsewhere)

    specific to home page:
    ----------------------
    featured_links : JSON - links to page redirects for the big buttons
    featured_events : links to one or more Event records
    featured_stats : lins to one or more Data records

    show_featured_events : boolean - whether to show featured events section
    show_featured_stats : boolean - whether to show featured stats section
    show_featured_links : boolean - whether to show featured links section
    show_featured_video : boolean - whether to show featured video

    featured_stats_description : str - descriptive text on what the stats are about
    featured_events_description : str - descriptive text on the featured events

    specific to the footer on all pages:
    ------------------------------------
    show_footer_subscribe : Boolean - whether to show newsletter subscribe box
    show_footer_social_media : Boolean - whether to show footer social media icons
    social_media_links: str
      Links to social media, such as:  ["facebook:www.facebook.com/coolerconcord/,instgram:www.instagram.com/coolerconcord/"]

    more_info: JSON - extraneous information
    is_deleted: boolean - whether this page was deleted from the platform (perhaps with it's community)
    is_published: boolean - whether this page is live
    is_template: boolean - whether this is a template to be copied

    """

    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    images = models.ManyToManyField(Media, related_name="homepage_images", blank=True)
    image_sequence = models.ForeignKey(
        ImageSequence, on_delete=models.DO_NOTHING, db_index=True, blank=True, null=True
    )

    featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    featured_links = models.JSONField(blank=True, null=True)
    featured_events = models.ManyToManyField(Event, blank=True)
    featured_stats = models.ManyToManyField(Data, blank=True)

    show_featured_events = models.BooleanField(default=True, blank=True)
    show_featured_stats = models.BooleanField(default=True, blank=True)
    show_featured_links = models.BooleanField(default=True, blank=True)
    show_featured_video = models.BooleanField(default=False, blank=True)

    featured_stats_subtitle = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    featured_stats_description = models.CharField(max_length=LONG_STR_LEN, blank=True)
    featured_events_subtitle = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    featured_events_description = models.CharField(max_length=LONG_STR_LEN, blank=True)

    show_footer_subscribe = models.BooleanField(default=True, blank=True)
    show_footer_social_media = models.BooleanField(default=True, blank=True)
    social_media_links = models.JSONField(blank=True, null=True)

    is_template = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "HomePageSettings - %s" % (self.community)

    def info(self):
        return model_to_dict(self, ["id", "title", "community"])

    def simple_json(self):
        res = model_to_dict(
            self, exclude=["images", "featured_events", "featured_stats", "community"]
        )
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        res = self.simple_json()
        images = self.images.all()
        sequence = self.image_sequence.sequence if self.image_sequence else None
        res["images"] = (
            get_images_in_sequence(images, json.loads(sequence))
            if sequence
            else [i.simple_json() for i in images]
        )
        res["community"] = get_summary_info(self.community)
        res["featured_events"] = [i.simple_json() for i in self.featured_events.all()]
        res["featured_stats"] = [i.simple_json() for i in self.featured_stats.all()]
        return res

    class Meta:
        db_table = "home_page_settings"
        verbose_name_plural = "HomePageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description", "featured_stats_description", "featured_events_description", "featured_stats_subtitle", "featured_events_subtitle"]


class ActionsPageSettings(models.Model):
    """
    Represents the community's Actions page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    images = models.ManyToManyField(Media, blank=True)
    featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    more_info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def simple_json(self):
        res = model_to_dict(self, exclude=["images"])
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        res = self.simple_json()
        res["images"] = [i.simple_json() for i in self.images.all()]
        return res

    def __str__(self):
        return "ActionsPageSettings - %s" % (self.community)

    class Meta:
        db_table = "actions_page_settings"
        verbose_name_plural = "ActionsPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class ContactUsPageSettings(models.Model):
    """
    Represents the community's ContactUs page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    images = models.ManyToManyField(Media, blank=True)
    featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    more_info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def simple_json(self):
        res = model_to_dict(self, exclude=["images"])
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        res = self.simple_json()
        res["images"] = [i.simple_json() for i in self.images.all()]
        return res

    def __str__(self):
        return "ContactUsPageSettings - %s" % (self.community)

    class Meta:
        db_table = "contact_us_page_settings"
        verbose_name_plural = "ContactUsPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class DonatePageSettings(models.Model):
    """
    Represents the communities Donate page settings.

    Attributes
    ----------
    see description under PageSettings

    one additional field:
    donation_link : str - link to donation url (if not contained within the HTML description)
    """

    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    images = models.ManyToManyField(Media, blank=True)
    featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    donation_link = models.CharField(max_length=LONG_STR_LEN, blank=True)
    more_info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def simple_json(self):
        res = model_to_dict(self, exclude=["images"])
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        res = self.simple_json()
        res["images"] = [i.simple_json() for i in self.images.all()]
        return res

    def __str__(self):
        return "DonatePageSettings - %s" % (self.community)

    class Meta:
        db_table = "donate_page_settings"
        verbose_name_plural = "DonatePageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class AboutUsPageSettings(models.Model):
    """
    Represents the community's AboutUs page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    images = models.ManyToManyField(Media, blank=True)
    # image = models.ForeignKey(Media, blank=True, null=True, on_delete=models.SET_NULL)
    featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    more_info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def simple_json(self):
        res = model_to_dict(self, exclude=["images"])
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        res = self.simple_json()
        # res['images'] = [i.simple_json() for i in self.images.all()]
        res["images"] = [i.simple_json() for i in self.images.all()]
        return res

    def __str__(self):
        return "AboutUsPageSettings - %s" % (self.community)

    class Meta:
        db_table = "about_us_page_settings"
        verbose_name_plural = "AboutUsPageSettings"
    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class ImpactPageSettings(models.Model):
    """
    Represents the community's Impact page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    sub_title = models.CharField(max_length=LONG_STR_LEN, blank=True)
    description = models.TextField(max_length=LONG_STR_LEN, blank=True)
    images = models.ManyToManyField(Media, blank=True)
    featured_video_link = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    more_info = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    is_published = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def simple_json(self):
        res = model_to_dict(self, exclude=["images"])
        res["community"] = get_summary_info(self.community)
        return res

    def full_json(self):
        res = self.simple_json()
        res["images"] = [i.simple_json() for i in self.images.all()]
        return res

    def __str__(self):
        return "ImpactPageSettings - %s" % (self.community)

    class Meta:
        db_table = "impact_page_settings"
        verbose_name_plural = "ImpactPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class TeamsPageSettings(PageSettings):
    """
    Represents the community's Teams page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    def __str__(self):
        return "TeamsPageSettings - %s" % (self.community)

    class Meta:
        db_table = "teams_page_settings"
        verbose_name_plural = "TeamsPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class VendorsPageSettings(PageSettings):
    """
    Represents the community's Vendors page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    def __str__(self):
        return "VendorsPageSettings - %s" % (self.community)

    class Meta:
        db_table = "vendors_page_settings"
        verbose_name_plural = "VendorsPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class EventsPageSettings(PageSettings):
    """
    Represents the community's Events page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    def __str__(self):
        return "EventsPageSettings - %s" % (self.community)

    class Meta:
        db_table = "events_page_settings"
        verbose_name_plural = "EventsPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class TestimonialsPageSettings(PageSettings):
    """
    Represents the community's Testimonials page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    def __str__(self):
        return "TestimonialsPageSettings - %s" % (self.community)

    class Meta:
        db_table = "testimonials_page_settings"
        verbose_name_plural = "TestimonialsPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class RegisterPageSettings(PageSettings):
    """
    Represents the community's Registration page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    def __str__(self):
        return "RegisterPageSettings - %s" % (self.community)

    class Meta:
        db_table = "register_page_settings"
        verbose_name_plural = "RegisterPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class SigninPageSettings(PageSettings):
    """
    Represents the community's Signin page settings.

    Attributes
    ----------
    see description under PageSettings
    """

    def __str__(self):
        return "SigninPageSettings - %s" % (self.community)

    class Meta:
        db_table = "signin_page_settings"
        verbose_name_plural = "SigninPageSettings"

    class TranslationMeta:
        fields_to_translate = ["title", "sub_title", "description"]


class Message(models.Model):
    """
    A class used to represent a Message sent on the MassEnergize Platform

    Attributes
    ----------

    """

    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)
    title = models.CharField(max_length=SHORT_STR_LEN)
    uploaded_file = models.ForeignKey(
        Media, blank=True, null=True, on_delete=models.SET_NULL
    )
    email = models.EmailField(blank=True)
    user = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True
    )
    body = models.TextField(max_length=LONG_STR_LEN)
    community = models.ForeignKey(
        Community, blank=True, on_delete=models.SET_NULL, null=True
    )
    team = models.ForeignKey(Team, blank=True, on_delete=models.SET_NULL, null=True)
    have_replied = models.BooleanField(default=False, blank=True)
    have_forwarded = models.BooleanField(default=False, blank=True)
    is_team_admin_message = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    archive = models.BooleanField(default=False, blank=True)
    starred = models.BooleanField(default=False, blank=True)
    response = models.CharField(max_length=LONG_STR_LEN, blank=True, null=True)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    schedule_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}"

    def simple_json(self):
        res = model_to_dict(self)
        res["community"] = get_summary_info(self.community)
        res["team"] = get_summary_info(self.team)
        res["user"] = get_summary_info(self.user)
        res["replies"] = [
            r.simple_json()
            for r in Message.objects.filter(parent=self, archive=False).order_by(
                "-created_at"
            )
        ]
        res["created_at"] = self.created_at.strftime("%Y-%m-%d %H:%M")
        return res

    def get_scheduled_message_info(self):
        scheduled_info = self.schedule_info or {}
        recipients = scheduled_info.get("recipients", {})
        audience = recipients.get("audience", None)
        audience_type = recipients.get("audience_type", None)
        community_ids = recipients.get("community_ids", None)

        real_audience = audience
        if audience and not audience == "all":
            if audience_type == "COMMUNITY_CONTACTS":
                real_audience = [c.info() for c in Community.objects.filter(id__in=audience.split(","))]

            elif audience_type == "ACTIONS":
                real_audience = [a.info() for a in Action.objects.filter(id__in=audience.split(","))]
            else:
                real_audience= [u.info() for u in UserProfile.objects.filter(id__in=audience.split(","))]
        if not item_is_empty(community_ids):
            community_ids = [c.info() for c in Community.objects.filter(id__in=community_ids.split(","))]
        else:
            community_ids = []

        scheduled_info["recipients"]["audience"] = real_audience
        scheduled_info["recipients"]["community_ids"] = community_ids

        return scheduled_info


    def full_json(self):
        res = self.simple_json()
        res["uploaded_file"] = get_json_if_not_none(self.uploaded_file)
        if self.schedule_info:
            res["schedule_info"] = self.get_scheduled_message_info()
        return res

    class Meta:
        ordering = ("title",)
        db_table = "messages"

    class TranslationMeta:
        fields_to_translate = ["title", "body"]


class ActivityLog(models.Model):
    """
    A class used to represent  Activity Log on the MassEnergize Platform

    Attributes
    ----------
    """

    id = models.AutoField(primary_key=True)
    path = models.CharField(max_length=SHORT_STR_LEN, default="/")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=SHORT_STR_LEN, default="success", blank=True)
    trace = models.JSONField(blank=True, null=True)
    request_body = models.JSONField(blank=True, null=True)

    # add response or error field

    def __str__(self):
        return self.path

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        res = self.simple_json()
        res["user"] = get_json_if_not_none(self.user)
        res["community"] = get_json_if_not_none(self.community)
        return res

    class Meta:
        ordering = ("path",)
        db_table = "activity_logs"


class Deployment(models.Model):
    """
    A class used to represent  Activity Log on the MassEnergize Platform

    Attributes
    ----------
    """

    id = models.AutoField(primary_key=True)
    version = models.CharField(max_length=SHORT_STR_LEN, default="")
    deploy_commander = models.CharField(
        max_length=SHORT_STR_LEN, default="", blank=True
    )
    notes = models.CharField(max_length=LONG_STR_LEN, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.version

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "deployments"
        ordering = ("-version",)


class FeatureFlag(models.Model):
    """
    A class used to represent Feature flags to turn on for
    communities and users

    scope : str - Whether this flag is for backend, admin frontend, of user frontend
    audience : str - (Communities) Whether the feature is for every community/ Specific Communities / or All, except some communities
    user_audience : str - (Users) Whether the feature is for every user/ Specific Users / or All, except some users
    key : str - A unique simple key that can be used to look up the particular feature
    communities :  Community - All communities involved  with the flag. Depending on the value of "audience" this could be a whitelist, or a blacklist
    users : User - All users involved with the flag. Depending on the value of "user_audience" this could be a whitelist or a blacklist
    notes : str - Any extra description worth noting
    expires_on : DateTime - When the feature should expire. Null value means feature will never expire
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
    scope = models.CharField(
        max_length=SHORT_STR_LEN, default=FeatureFlagConstants.for_user_frontend()
    )  # Is Backend/AdminFrontend/Portal Frontend etc.
    audience = models.CharField(
        max_length=SHORT_STR_LEN, default=FeatureFlagConstants.for_everyone()
    )  # Community Audience: For Everyone/ Specific Communities / Or Everyone Except
    user_audience = models.CharField(
        max_length=SHORT_STR_LEN, default=FeatureFlagConstants.for_everyone()
    )  # User Audience: For Everyone/ Specific Communities / Or Everyone Except
    key = models.CharField(
        max_length=SHORT_STR_LEN, unique=True
    )  # Special key that "makes sense", and we can use for easy look-up (will be autogenerated on F.E) Eg. (guest_authentication_feature)
    communities = models.ManyToManyField(
        Community, blank=True, related_name="community_feature_flags"
    )
    users = models.ManyToManyField(
        UserProfile, blank=True, related_name="user_feature_flags"
    )
    notes = models.CharField(max_length=LONG_STR_LEN, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(null=True, blank=True)
    allow_opt_in = models.BooleanField(default=False, blank=True) #This field will be used to determine if a community admins can opt in to a feature flag

    def __str__(self):
        return f"{self.name}"

    def info(self):
        return {"id": self.id, "name": self.name, "key": self.key,}

    def simple_json(self):
        res = model_to_dict(
            self,
            fields=[
                "id",
                "name",
                "expires_on",
                "audience",
                "user_audience",
                "key",
                "scope",
                "notes",
                "allow_opt_in"
            ],
        )
        res["communities"] = [
            {"id": c.id, "name": c.name} for c in self.communities.all()
        ]
        return res

    def full_json(self):
        res = model_to_dict(self, exclude=["communities", "users"])
        res["communities"] = [
            {"id": c.id, "name": c.name} for c in self.communities.all()
        ]
        res["users"] = [
            {"id": u.id, "preferred_name": u.preferred_name, "email": u.email}
            for u in self.users.all()
        ]
        return res


    def is_enabled_for_community(self, community: Community):
        """
        Returns : True if the feature flag is enabled for the community
        """
        if self.audience == FeatureFlagConstants.for_everyone():
            return True
        elif self.audience == FeatureFlagConstants.for_specific_audience():
            return self.communities.filter(id=community.id).exists()
        elif self.audience == FeatureFlagConstants.for_all_except():
            return not self.communities.filter(id=community.id).exists()
        return False

    def enabled(self):
        current_date_and_time = datetime.datetime.now(timezone.utc)
        if self.expires_on and self.expires_on < current_date_and_time:
            return False  # flag not active
        return True

    def enabled_communities(self, communities_in: QuerySet = None):
        """
              Returns : List of communities as a QuerySet
          """
        if not communities_in:
            communities_in = Community.objects.filter(is_deleted=False)

        community_ids = self.communities.values_list('id', flat=True)

        if self.audience == "EVERYONE":
            return communities_in
        elif self.audience == "SPECIFIC":
            return communities_in.filter(id__in=community_ids)
        elif self.audience == "ALL_EXCEPT":
            return communities_in.exclude(id__in=community_ids)

        return []

    def enabled_users(self, users_in: QuerySet):
        if self.user_audience == "EVERYONE":
            return users_in
        elif self.user_audience == "SPECIFIC":
            return users_in.filter(id__in=[str(u.id) for u in self.users.all()])
        elif self.user_audience == "ALL_EXCEPT":
            return users_in.exclude(id__in=[str(u.id) for u in self.users.all()])
        return None

    class Meta:
        db_table = "feature_flags"
        ordering = ("-name",)


class Footage(models.Model):
    """
    A class that is used to represent a record of an activity that a user has performed on any of of the ME platforms


    actor: Signed in user who performs the activity
    type: The kind of activity that was just performed. Check FootageConstants.py(TYPES) for a list of all available activity types
    portal: Which platform the activity happens on Check FootageConstants.py(PLATFORMS) for a list of available platforms
    description: A brief description of what happened in the activity E.g User405 deleted action with id 444
    users : other users who are involved in the activity. (E.g an admin makes 3 other admins admin of a community. The "3 other" admins will be found here... )
    communities: The communities that are directly involved in the activity that took place. E.g - A user is Cadmin of 3 communities, and deletes an action. Only the communities that are linked to action will be linked here.
    by_super_admin: Just a field that lets you easily know the activity is a Sadmin activity
    item_type: Whether footage is related to an action, event, testimonial, a community, etc.
    activity_type: Whether its Sign in, deletion, update, creation etc.
    """

    id = models.AutoField(primary_key=True)
    actor = models.ForeignKey(
        UserProfile,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=True,
        related_name="footages",
    )
    activity_type = models.CharField(max_length=SHORT_STR_LEN, null=False)
    portal = models.CharField(
        max_length=SHORT_STR_LEN, default=FootageConstants.on_admin_portal()
    )
    notes = models.CharField(max_length=LONG_STR_LEN, default="", blank=True)
    related_users = models.ManyToManyField(
        UserProfile, blank=True, related_name="appearances"
    )
    communities = models.ManyToManyField(Community, blank=True)
    by_super_admin = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    actions = models.ManyToManyField(Action, blank=True)
    testimonials = models.ManyToManyField(Testimonial, blank=True)
    teams = models.ManyToManyField(Team, blank=True)
    events = models.ManyToManyField(Event, blank=True)
    images = models.ManyToManyField(Media, blank=True)
    messages = models.ManyToManyField(Message, blank=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    item_type = models.CharField(
        max_length=SHORT_STR_LEN, null=True, blank=True, default=""
    )

    def simple_json(self):
        data = model_to_dict(
            self,
            fields=["activity_type", "notes", "portal", "item_type", "by_super_admin"],
        )
        data["actor"] = self.actor.info() if self.actor else None
        data["created_at"] = self.created_at
        data["communities"] = (
            [c.info() for c in self.communities.all()] if self.communities else []
        )
        data = FootageConstants.change_type_to_boolean(data)

        return data

    def full_json(self):
        return self.simple_json()

    def __str__(self) -> str:
        return f"{self.actor.preferred_name} - {self.activity_type} - {self.item_type}"

    class Meta:
        db_table = "footages"
        ordering = ("-id",)

    class TranslationMeta:
        fields_to_translate = ["notes"]


class CommunityNotificationSetting(models.Model):

    COMMUNITY_NOTIFICATION_TYPES_CHOICES = [(item, item) for item in COMMUNITY_NOTIFICATION_TYPES]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="notification_settings",related_query_name="notification_setting")
    updated_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    notification_type = models.CharField(max_length=SHORT_STR_LEN, null=False, blank=False,choices=COMMUNITY_NOTIFICATION_TYPES_CHOICES)
    is_active = models.BooleanField(default=True, blank=True)
    activate_on = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    more_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.community.name} - {self.notification_type}"

    def info(self):
        return {"id": self.id, "is_active": self.is_active, "activate_on": str(self.activate_on) if self.activate_on else self.activate_on, "notification_type": self.notification_type,}

    def simple_json(self):
        return {"id": self.id, "notification_type": self.notification_type, "is_active": self.is_active,
                "activate_on": str(self.activate_on) if self.activate_on else self.activate_on}

    def full_json(self):
        data = self.simple_json()
        data["community"] = self.community.info()
        data["updated_by"] = self.updated_by.info() if self.updated_by else None
        return data

    class Meta:
        indexes = [ models.Index(fields=["community", "notification_type"]),]

    class TranslationMeta:
        fields_to_translate = ["notification_type"]


# localisation
class SupportedLanguage(BaseModel):
    """
    A class used to represent the languages supported by the platform

    Attributes
    ----------
    name : str
      name of the language.
    code : str

    """

    code = models.CharField(max_length=LANG_CODE_STR_LEN, unique=True)
    name = models.CharField(max_length=SHORT_STR_LEN, unique=True)
    is_right_to_left = models.BooleanField(default=False, blank=True) # not used now but maybe used in the future

    def __str__(self):
        return self.name


    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "supported_languages"
        ordering = ("name",)


class CommunitySupportedLanguage(BaseModel):
    """
    A class used to represent the languages supported by the platform

    Attributes
    ----------
    community : int Foreign key to the community
    language : int Foreign key to the supported language
    """

    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    language = models.ForeignKey(SupportedLanguage, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return f"{self.community.name} - {self.language.name}"

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "community_supported_languages"
        unique_together = ["community", "language"]
        ordering = ("community", "language")


class TranslationsCache(BaseModel):
    """
    A class used to represent the translations cache table

    Attributes
    ----------
    hash	: str
    source_language_code  : str
    target_language_code  : str
    translated_text	: str
    last_translated	: DateTime
    """
    hash = models.CharField(max_length=SHORT_STR_LEN)
    source_language_code = models.CharField(max_length=LANG_CODE_STR_LEN)
    target_language_code = models.CharField(max_length=LANG_CODE_STR_LEN)
    translated_text = models.TextField(max_length=LONG_STR_LEN)
    last_translated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hash}: {self.translated_text}"

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "translations_cache"


class ManualCommunityTranslation(TranslationsCache):
    """
    A class used to represent the manual translations done by the community

    Attributes
    ----------
    community : str
    """

    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)

    class Meta:
        db_table = "manual_community_translations"


class CampaignSupportedLanguage(BaseModel):
    language = models.ForeignKey(SupportedLanguage, on_delete=models.CASCADE, db_index=True)
    campaign = models.ForeignKey("apps__campaigns.Campaign", on_delete=models.CASCADE, db_index=True, related_name="supported_languages")
    is_active = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return f"{self.campaign.title} - {self.language.name}"

    def simple_json(self):
        return {"id": str(self.id), "is_active": self.is_active, "campaign": str(self.id), "code": self.language.code, "name": self.language.name}

    def full_json(self):
        return self.simple_json()

    class Meta:
        db_table = "campaign_supported_languages"


class TestimonialAutoShareSettings(BaseModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, db_index=True)
    share_from_communities = models.ManyToManyField(Community, related_name="share_from_communities", blank=True)
    share_from_location_type = models.CharField(max_length=SHORT_STR_LEN, choices = LocationType.choices(), default=LocationType.CITY.value[0])
    share_from_location_value = models.CharField(max_length=SHORT_STR_LEN, blank=True)
    excluded_tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.community.name} - {[community.name for community in self.share_from_communities.all()]}"

    def simple_json(self):
        return model_to_dict(self)

    def full_json(self):
        return self.simple_json()
