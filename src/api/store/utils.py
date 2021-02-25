from database.models import Community, UserProfile, RealEstateUnit, Location
from _main_.utils.massenergize_errors import CustomMassenergizeError, InvalidResourceError
from _main_.utils.context import Context
from django.db.models import Q
from database.utils.constants import SHORT_STR_LEN
import requests 
import json
import zipcodes
from sentry_sdk import capture_message

def get_community(community_id=None, subdomain=None):
  try:
    if community_id:
      return Community.objects.filter(pk=community_id).first(), None
    elif subdomain: 
      return Community.objects.filter(subdomain=subdomain).first(), None
  except Exception as e:
    capture_message(str(e), level="error")
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
    capture_message(str(e), level="error")
    return None, CustomMassenergizeError(e)


def get_community_or_die(context, args):
  subdomain = args.pop('subdomain', None)
  community_id = args.pop('community_id', None)

  if not community_id and not subdomain:
    raise Exception("Missing community_id or subdomain field")
  elif community_id:
    return Community.objects.get(pk=community_id)
  elif subdomain:
    return Community.objects.get(subdomain=subdomain)
  else:
    raise Exception("Please provide a valid community_id or subdomain")
  

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
    return []
  user = UserProfile.objects.get(pk=context.user_id)
  admin_groups = user.communityadmingroup_set.all()
  communities = [ag.community for ag in admin_groups]
  return communities, None


def send_slack_message(webhook, body):
  r = requests.post(url = webhook, data = json.dumps(body)) 
  return r

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
  Given an old title for an action to be copied, it will generate a new one 
  for use by a clone of the same actuon
  # remove the "TEMPLATE", "TEMP" or "TMP" prefix or suffix
  """
  new_title = old_title

  loc = old_title.find("TEMPLATE")
  if loc == 0 :
    new_title = old_title[9:]
  elif loc > 0:
    new_title = old_title[0:loc-1]
  else:
    loc = old_title.find("TEMP")
    if loc==0:
      new_title = old_title[5:]
    elif loc>0:
      new_title = old_title[0:loc-1]
    else:
      loc = old_title.find("TMP")
      if loc==0:
        new_title = old_title[4:]
      elif loc>0:
        new_title = old_title[0:loc-1]

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
  for location in community.location_set.all():
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
      if reu_community_type != 'ZIPCODE' and reu_community_type != 'CITY' and reu_community_type != 'COUNTY' and reu_community_type != 'STATE':
        reu_loc_data = zipcodes.matching(zip)
        if len(reu_loc_data)>0 and reu_loc_data[0]['country']==location.country:           
          if verbose: print("Found REU with zipcode "+zip+" within community: "+community.name)
          return True

  return False
