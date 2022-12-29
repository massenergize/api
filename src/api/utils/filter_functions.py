import json
import operator
from functools import reduce
from django.db.models import Q


def get_events_filter_params(params):
    try:
      params= json.loads(params)
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
      params= json.loads(params)
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
      params= json.loads(params)
      
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
       query.append(Q(tags__name__in=tags))
      if not status == None:
       query.append(Q(is_published=status))

      return query
    except Exception as e:
      return []


def get_communities_filter_params(params):
    try:
      params= json.loads(params)
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