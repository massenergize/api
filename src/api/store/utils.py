from zoneinfo import ZoneInfo
from _main_.settings import IS_LOCAL, IS_PROD, IS_CANARY
from _main_.utils.metrics import timed
from _main_.utils.utils import strip_website
from database.models import Community, UserProfile, RealEstateUnit, Location, CustomCommunityWebsiteDomain
from _main_.utils.massenergize_errors import CustomMassenergizeError, InvalidResourceError
from _main_.utils.context import Context
from django.db.models import Q
from django.core.files.uploadedfile import InMemoryUploadedFile
from database.utils.constants import SHORT_STR_LEN
import zipcodes
import datetime
from carbon_calculator.carbonCalculator import AverageImpact
from _main_.utils.massenergize_logger import log


def getCarbonScoreFromActionRel(actionRel): 
  if not actionRel or actionRel.status !="DONE":  return 0 
  if actionRel.carbon_impact : return actionRel.carbon_impact
  calculator_action = actionRel.action.calculator_action
  if calculator_action: 
      return AverageImpact(calculator_action, actionRel.date_completed)
  return 0

def get_community(community_id=None, subdomain=None):
  try:
    if community_id:
      return Community.objects.filter(pk=community_id).first(), None
    elif subdomain: 
      return Community.objects.filter(subdomain=subdomain).first(), None
  except Exception as e:
    log.exception(e)
    return None, CustomMassenergizeError(e)

  return None, CustomMassenergizeError("Missing community_id or subdomain field")

def get_user(user_id, email=None):
  try:
    if email: 
      return UserProfile.objects.filter(email=email).first(), None
    elif user_id:
      return UserProfile.objects.filter(pk=user_id).first(), None
    return None, CustomMassenergizeError("Missing user_id or email field")
  except Exception as e:
    log.exception(e)
    return None, CustomMassenergizeError(e)

@timed
def get_community_or_die(context: Context, args) -> Community:
  subdomain = args.pop('subdomain', None)
  community_id = args.pop('community_id', None)
  referrer_website = context.request.META.get('HTTP_REFERER')

  community = None
  if community_id:
    community = Community.objects.select_related("logo", "favicon", "goal").filter(pk=community_id).first()
  elif subdomain and subdomain != 'home':
    community = Community.objects.select_related("logo", "favicon", "goal").filter(subdomain__iexact=subdomain).first()

  elif referrer_website:
    # since we dont have a subdomain or community_id, we will fall back to the referrer site
    website = strip_website(referrer_website)
    community_website = CustomCommunityWebsiteDomain.objects.select_related("community").filter(website__iexact=website).first()
    if community_website:
      community = community_website.community
    elif website.endswith("massenergize.org") or website.endswith("massenergize.dev"):
      domain_components = website.split(".")
      if len(domain_components) >= 3:
        # if there is a subdomain there will be at least three parts
        subdomain = domain_components[0]
        community = Community.objects.select_related("logo", "favicon", "goal").filter(subdomain__iexact=subdomain).first()

  if not community:
    # we explored all our options and could not get a community
    raise Exception("Please provide a valid community_id or subdomain")

  return community

def get_user_or_die(context, args):
  user_email = args.pop('user_email', None) or args.pop('email', None) 
  user_id = args.pop('user_id', None) 
  if user_id:
    return UserProfile.objects.get(pk=user_id)
  elif user_email:
    return UserProfile.objects.get(email=user_email)
  elif context.user_id:
    return UserProfile.objects.get(pk=context.user_id)
  elif context.user_email:
    return UserProfile.objects.get(email=context.user_email)
  else:
    raise Exception("Please provide a valid user_id or user_email")


def get_admin_communities(context: Context):
  if not context.user_is_logged_in and context.user_is_admin():
    return [], None
  user = UserProfile.objects.get(pk=context.user_id)
  admin_groups = user.communityadmingroup_set.all()
  communities = [ag.community for ag in admin_groups]
  return communities, None


def remove_dups(lst):
  final_lst = []
  tracking_set = set()
  
  for u in lst:
    if u not in tracking_set:
      final_lst.append(u)
      tracking_set.add(u)
  
  return final_lst

def get_new_title(new_community, old_title):
  """
  Given an old title or name for an action, event or vendor to be copied, it will generate a new one 
  for use by a clone of the same action, event or vendor
  # remove the "TEMPLATE", "TEMP" or "TMP" prefix or suffix
  """
  new_title = old_title

  loc = old_title.find("TEMPLATE")
  if loc == 0 :
    new_title = old_title[9:]
  elif loc > 0:
    new_title = old_title[0:loc]
  else:
    loc = old_title.find("TEMP")
    if loc==0:
      new_title = old_title[5:]
    elif loc>0:
      new_title = old_title[0:loc]
    else:
      loc = old_title.find("TMP")
      if loc==0:
        new_title = old_title[4:]
      elif loc>0:
        new_title = old_title[0:loc]

  if not new_community: return new_title

  # add community name to suffix (not the action id
  # #make sure the action title does not exceed the max length expected
  suffix = f'-{new_community.subdomain}'
  len_suffix = len(suffix)
  new_title_len = min(len(new_title), SHORT_STR_LEN - len_suffix)
  return new_title[0:new_title_len]+suffix


def find_reu_community(reu, verbose=False):
  """
  Determine which, if any, community this household is actually in
  """
  communities = Community.objects.filter(is_deleted=False, is_geographically_focused=True)

  # heirarchy of communities:
  # most communities will be Zipcode
  communities1 = communities.filter(geography_type='ZIPCODE')
  for community in communities1:
    if is_reu_in_community(reu, community, verbose):
      return community

  communities1 = communities.filter(geography_type='CITY')
  for community in communities1:
    if is_reu_in_community(reu, community, verbose):
      return community

  communities1 = communities.filter(geography_type='COUNTY')
  for community in communities1:
    if is_reu_in_community(reu, community, verbose):
      return community

  communities1 = communities.filter(geography_type='STATE')
  for community in communities1:
    if is_reu_in_community(reu, community, verbose):     
      return community

  communities1 = communities.filter(geography_type='COUNTRY')
  for community in communities1:
    if is_reu_in_community(reu, community, verbose):
      return community

  return None

def is_reu_in_community(reu, community, verbose=False):
  """
  Determine whether the RealEstateUnit reu is in community
  """

  if reu.address:
    zip = reu.address.zipcode
    if not zip:
      if verbose: print("RealEstateUnit address doesn't include zipcode")
      return False
  else:
    if verbose: print("RealEstateUnit doesn't have address")
    return False

  geography_type = community.geography_type
  reu_community_type = None
  if reu.community:   # current community REU linked to
    reu_community_type = reu.community.geography_type

  # loop over the locations linked to in the community, to see if REU is in it
  for location in community.locations.all():
    if geography_type == 'ZIPCODE':
      if zip==location.zipcode:
        if verbose: print("Found REU with zipcode "+zip+" within community: "+community.name)
        return True

    elif geography_type == 'CITY':
      # check if reu in city if not within a smaller zipcode based community
      if reu_community_type != 'ZIPCODE':
        reu_loc_data = zipcodes.matching(zip)
        if len(reu_loc_data)>0 and reu_loc_data[0]['city']==location.city: 
          if verbose: print('Found REU with zipcode '+zip+" within community: "+community.name)
          return True

    elif geography_type == 'COUNTY':
      if reu_community_type != 'ZIPCODE' and reu_community_type != 'CITY':
        reu_loc_data = zipcodes.matching(zip)
        if len(reu_loc_data)>0 and reu_loc_data[0]['county']==location.county:           
          if verbose: print("Found REU with zipcode "+zip+" within community: "+community.name)
          return True

    elif geography_type == 'STATE':
      if reu_community_type != 'ZIPCODE' and reu_community_type != 'CITY' and reu_community_type != 'COUNTY':
        reu_loc_data = zipcodes.matching(zip)
        if len(reu_loc_data)>0 and reu_loc_data[0]['state']==location.state:           
          if verbose: print("Found REU with zipcode "+zip+" within community: "+community.name)
          return True

    elif geography_type == 'COUNTRY':

      # special catch-all case for RealEstateUnits with invalid zipcodes, which get set to "00000"
      if location.country=="US" and zip=="00000":
          if verbose: print("Found REU with zipcode "+zip+" within community: "+community.name)
          return True


      if reu_community_type != 'ZIPCODE' and reu_community_type != 'CITY' and reu_community_type != 'COUNTY' and reu_community_type != 'STATE':
        reu_loc_data = zipcodes.matching(zip)
        if len(reu_loc_data)>0 and reu_loc_data[0]['country']==location.country:           
          if verbose: print("Found REU with zipcode "+zip+" within community: "+community.name)
          return True

  return False

def split_location_string(loc):
  """
  Return the parts of a location string (formerly used for a real estate unit location)
  """
  return loc.capitalize().replace(", ", ",").split(",")

def check_location(street, unit, city, state, zipcode, county="", country="US"):
  """
  Check that an address is valid (zip code if in US)
  """
  # check zipcode if US location
  if country == 'US':
    if not zipcode and not city and not state and not county:
      return "No zipcode, city, state or county provided", False
    elif zipcode == "00000":
      # not a real zipcode, but use for unknown zipcode in US
      # this is for previously entered zipcodes which may have been invalid
      pass
    else :
      try:
        matching_locations = zipcodes.matching(zipcode)
        if len(matching_locations) < 1:
          # No matching location
          return "Zipcode doesn't correspond to a community in US", False
      except Exception as e:
        return str(e), False

  else:
    # non US address, not currently supported
    return "Non-US addresses not currently supported", False

  
  location_type = 'FULL_ADDRESS'
  if zipcode and not street:
    location_type = 'ZIP_CODE_ONLY'
  elif state and not zipcode and not city and not county:
    location_type = 'STATE_ONLY'
  elif city and not zipcode and not street:
    location_type = 'CITY_ONLY'
  elif county and not city:
    location_type = 'COUNTY_ONLY'
  elif country and not state:
    location_type = 'COUNTRY_ONLY'
  return location_type, True

def unique_media_filename(file):
  if type(file) != InMemoryUploadedFile:
    raise Exception("Unexpected file type for media image file")
    
  unique_datetime = datetime.datetime.now().strftime("-%y%m%d-%H%M%S")
  dot = file.name.rfind(".")
  if dot>0:
    filename = file.name[0:dot] + unique_datetime + file.name[dot:]
  else:
    filename = file.name + unique_datetime
  return filename



def get_user_from_context(context):
  if not context:
    return None
  if context.user_id:
    return UserProfile.objects.filter(id=context.user_id).first()
  elif context.user_email:
    return UserProfile.objects.filter(email=context.user_email).first()
  return None


#def get_frontend_host(): 
#  if IS_PROD: 
#    return "https://admin.massenergize.org/" 
#  elif IS_CANARY: 
#    return "" # Replace wwhen you get the cannary frontend admin URL
#  elif IS_LOCAL: 
#    return "http://localhost:3001/"
#  else: 
#    return "https://admin.massenergize.dev/"


def get_human_readable_date(date):
  if not date:
    return "N/A"
  formatted_datetime = date.strftime("%d %B %Y, %I:%M %p")
  day_suffix = "th" if 11 <= date.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(date.day % 10, "th")
  formatted_datetime = formatted_datetime.replace("{:02d}".format(date.day), "{:d}{}".format(date.day, day_suffix))
  return formatted_datetime



def get_massachusetts_time(date_and_time):
    """
    Converts a UTC datetime string to local datetime in Massachusetts time zone.
    """    # Parse the datetime string to a datetime object
    try:
        # Try parsing the datetime string with the first format
        dt = datetime.datetime.strptime(str(date_and_time), '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        # If it fails, try the second format
        dt = datetime.datetime.strptime(str(date_and_time), '%Y-%m-%d %H:%M:%S%z')
    # Specify the Massachusetts time zone
    massachusetts_zone = ZoneInfo('America/New_York')

    # Convert time zone from UTC to Massachusetts time zone
    local_datetime = dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(massachusetts_zone)
    return local_datetime