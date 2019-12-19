from database.models import Community, UserProfile
from _main_.utils.massenergize_errors import CustomMassenergizeError, InvalidResourceError
from django.db.models import Q

def get_community(community_id=None, subdomain=None):
  try:
    if community_id:
      return Community.objects.filter(pk=community_id).first(), None
    elif subdomain: 
      return Community.objects.filter(subdomain=subdomain).first(), None
  except Exception as e:
    return None, CustomMassenergizeError(e)

  return None, CustomMassenergizeError("Missing community_id or subdomain field")

def get_user(user_id, email):
  try:
    if email: 
      return UserProfile.objects.filter(email=email).first(), None
    elif user_id:
      return UserProfile.objects.filter(pk=user_id).first(), None
    return None, CustomMassenergizeError("Missing user_id or email field")
  except Exception as e:
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
  user_email = args.pop('user_email', None) or args.pop('email', None) or context.user_email
  user_id = args.pop('user_id', None) or context.user_id
  user = None
  if user_id:
    return UserProfile.objects.get(pk=user_id)
  elif user_email:
    return UserProfile.objects.get(email=user_email)
  else:
    raise Exception("Please provide a valid user_id or user_email")

