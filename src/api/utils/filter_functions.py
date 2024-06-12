import datetime
import json
import operator
from functools import reduce
from django.db.models import Q

from database.models import CommunityMember


def get_events_filter_params(params):
    try:
      search_text = params.get("search_text", None)

      query = []
      communities = params.get("community", None)
      tags= params.get("tags",None)
      status = None
      if search_text:
        search= reduce(operator.or_,
         (Q(name__icontains= search_text),
         Q(community__name__icontains= search_text),
         Q(tags__name__icontains= search_text),
         ))
        query.append(search)
      if  "Yes" in params.get("live", []):
        status=True
      elif "No" in params.get("live",[]):
        status=False
      if communities:
        query.append(Q(community__name__in=communities))
      if tags:
       query.append(Q(tags__name__in=tags))
      if not status == None:
       query.append(Q(is_published=status))
      return query
    except Exception as e:
      return []


def get_testimonials_filter_params(params):
    try:
      search_text = params.get("search_text", None)
      
      query = []
      communities = params.get("community", None)
      action= params.get("action",None)
      status = None
      is_approved = None

      if search_text:
        search= reduce(operator.or_, (Q(title__icontains= search_text),Q(community__name__icontains= search_text),Q(user__full_name__icontains= search_text),Q(action__title__icontains= search_text),))
        query.append(search)
      if  "Yes" in params.get("live", []):
        status=True
      elif "No" in params.get("live",[]):
        status=False
      elif "Not Approved" in params.get("live",[]):
        is_approved=False
      if communities:
        query.append(Q(community__name__in=communities))
      if action:
       query.append(Q(action__title__icontains=action[0]))
      if status != None:
       query.append(Q(is_published=status))
      if not is_approved == None:
       query.append(Q(is_approved=is_approved))

      return query
    except Exception as e:
      return []


def get_actions_filter_params(params):
    try:
      
      search_text = params.get("search_text", None)
      query = []
      communities = params.get("community", None)
      tags= params.get("tags",None)
      status = None

      if search_text:
        search= reduce(operator.or_, 
        (Q(title__icontains= search_text),
        Q(tags__name__icontains= search_text),
        Q(community__name__icontains= search_text),
        ))
        query.append(search)

      if  "Yes" in params.get("live", []):
        status=True
      elif "No" in params.get("live",[]):
        status=False
      if communities:
        query.append(Q(community__name__in=communities))
      if tags:
       query.append(Q(tags__name__in=tags) or Q(tags__tag_collection__name__in=tags))
      if not status == None:
       query.append(Q(is_published=status))

      return query
    except Exception as e:
      return []


def get_communities_filter_params(params):
    try:
      search_text = params.get("search_text", None)
      query = []
      names = params.get("name", None)
      geographic = params.get("geography", None)
      if search_text:
        search= reduce(
        operator.or_, (
        Q(name__icontains= search_text),
        Q(owner_name__icontains= search_text),
        Q(owner_email__icontains= search_text),
        ))
        query.append(search)

      if "Verified" in params.get("verification", []):
        query.append(Q(is_approved=True))

      elif "Not Verified" in params.get("verification",[]):
          query.append(Q(is_approved=False))

      if names:
        query.append(Q(name__in=names))

      if geographic:
        if "Geographically Focused" in geographic:
            query.append(Q(is_geographically_focused=True))
        else:
            query.append(Q(is_geographically_focused=False))
      return query
    except Exception as e:
      return []



def get_messages_filter_params(params):
    try:
      query = []
      communities = params.get("community", None)
      teams = params.get("team", None)
      status = None
      forwarded =None
      is_scheduled = params.get("is_scheduled", None)
      
      search_text = params.get("search_text", None)
      if search_text:
        search= reduce(
        operator.or_, (
        Q(title__icontains= search_text),
        Q(community__name__icontains= search_text),
        Q(team__name__icontains= search_text),
        Q(user__full_name__icontains= search_text),
        Q(user_name__icontains= search_text),
        ))
        query.append(search)

      if  "Yes" in params.get("replied?", []):
        status=True
      elif "No" in params.get("replied?",[]):
        status=False

      if "Yes" in params.get("forwarded to team admin?", []):
        forwarded= True
      if "No" in params.get("forwarded to team admin?", []):
        forwarded= False


      if is_scheduled:
        query.append(Q(scheduled_at__isnull=False) & Q(scheduled_at__gt=datetime.datetime.now()))

      if communities:
        query.append(Q(community__name__in=communities))
      if teams:
        query.append(Q(team__name__in=teams))
      if not status == None:
       query.append(Q(have_replied=status))

      if not forwarded == None:
       query.append(Q(have_forwarded=forwarded))


      return query
    except Exception as e:
      return []


def get_teams_filter_params(params):
    try:

      query = []
      communities = params.get("community", None)
      parents = params.get("parent", None)
      status = None

      search_text = params.get("search_text", None)
      if search_text:
        search= reduce(
        operator.or_, (
        Q(name__icontains= search_text),
        Q(primary_community__name__icontains= search_text),
        Q(parent__name__icontains= search_text),
        ))
        query.append(search)
      
      if  "Yes" in params.get("live", []):
        status=True
      elif "No" in params.get("live",[]):
        status=False

      if communities:
        query.append(Q(communities__name__in=communities))
      if parents:
        query.append(Q(parent__name__in=parents))
      if not status == None:
       query.append(Q(is_published=status))

      return query
    except Exception as e:
      return []


def get_team_member_filter_params(params):
    try:
      query = []
      member_type = params.get("status", None)
      is_admin = None

      search_text = params.get("search_text", None)
      if search_text:
        search= reduce(
        operator.or_, (
        Q(user__full_name__icontains= search_text),
        Q(user__email__icontains= search_text),
        ))
        query.append(search)
      
      if  "Admin" in member_type:
        is_admin = True
      elif "Member" in member_type:
        is_admin=False

      if not is_admin == None:
       query.append(Q(is_admin=is_admin))

      return query
    except Exception as e:
      return []


def get_subscribers_filter_params(params):
    try:
      query = []
      search_text = params.get("search_text", None)
      if search_text:
        search= reduce(
        operator.or_, (
        Q(name__icontains= search_text),
        Q(community__name__icontains= search_text),
        Q(email__icontains= search_text),
        ))
        query.append(search)

      communities = params.get("community", None)
      if communities:
        query.append(Q(community__name__in=communities))

      return query
    except Exception as e:
      return []


def get_vendor_filter_params(params):
    try:
      query = []
      search_text = params.get("search_text", None)

      if search_text:
        search= reduce(
        operator.or_, (
        Q(name__icontains= search_text),
        Q(communities__name__icontains= search_text),
        Q(email__icontains= search_text),
        Q(service_area__icontains= search_text),
        ))
        query.append(search)
  
      communities = params.get("communities serviced", None)
      service_area= params.get('service area',None)

      if communities:
        query.append(Q(communities__name__icontains=communities[0]))
      if service_area:
       query.append(Q(service_area__in=service_area))

      return query
    except Exception as e:
      return []


def get_users_filter_params(params):
    try:
      query = []
      search_text = params.get("search_text", None)
      if search_text:
        users = CommunityMember.objects.filter(community__name__icontains=search_text).values_list('user', flat=True).distinct()
        search= reduce(
        operator.or_, (
        Q(full_name__icontains= search_text),
        Q(Q(id__in=users)),# 
        Q(email__icontains= search_text),
        ))
        query.append(search)

      communities = params.get("community", None)

      if communities:
        users = CommunityMember.objects.filter(community__name__in=communities).values_list('user', flat=True).distinct()
        query.append(Q(id__in=users))

      if  "Community Admin" in params.get("membership", []):
        query.append(Q(is_community_admin=True))
      elif "Super Admin" in params.get("membership",[]):
        query.append(Q(is_super_admin=True))
      elif "Member" in params.get("membership",[]):
          query.append(Q(is_super_admin=False,is_community_admin=False) )
 
      return query
    except Exception as e:
      return []



def get_tag_collections_filter_params(params):
    try:
      query = []
      search_text = params.get("search_text", None)
      if search_text:
        search= reduce(
        operator.or_, (
        Q(name__icontains= search_text),
        ))
        query.append(search)
        
      return query
    except Exception as e:
      return []


def get_super_admins_filter_params(params):
    try:
      query = []
      search_text = params.get("search_text", None)
      if search_text:
        search = reduce(
            operator.or_, (
                Q(full_name__icontains=search_text),
                Q(communities__name__icontains=search_text),
                Q(email__icontains=search_text),
            ))
        query.append(search)
        
      return query
    except Exception as e:
      return []




def get_sort_params(params):
  try:
    sort_params = params.get("sort_params", None)
    sort =""
    if sort_params:
      sort+= sort_params.get("name")
      if sort_params.get("direction") == "desc":
        sort = "-"+sort
      return sort.lower()
    
    return "-id"


  except Exception as e:
    return '-id'




def sort_items(queryset, params):
  if not queryset:
    return []
  if isinstance(queryset, list):
    return queryset

  sort_params = get_sort_params(params)
  return queryset.order_by(sort_params)