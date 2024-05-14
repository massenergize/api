"""
This contains custom decorators that can be used to check that specific
conditions have been satisfied
"""
from django.core.exceptions import PermissionDenied
from _main_.utils.context import Context
from functools import wraps
from django.views.decorators.http import require_http_methods
from django.core.cache import cache

from _main_.utils.massenergize_errors import CustomMassenergizeError

def login_required(function):
  """
  This decorator enforces that a user is logged in before a view can run
  """

  @wraps(function)
  def wrap(handler, request, *args, **kwargs):
    context: Context = request.context
    if context.user_is_logged_in:
      return function(handler, request, *args, **kwargs)
    else:
      raise PermissionDenied

  wrap.__doc__ = function.__doc__
  wrap.__name__ = function.__name__
  return wrap

def admins_only(function):
  """
  This decorator enforces that the user is an admin before the view can run
  """

  @wraps(function)
  def wrap(handler, request, *args, **kwargs):
    context: Context = request.context
    if context.user_is_logged_in and context.user_is_admin():
      return function(handler, request, *args, **kwargs)
    else:
      raise PermissionDenied

  wrap.__doc__ = function.__doc__
  wrap.__name__ = function.__name__
  return wrap

def community_admins_only(function):
  """
  This decorator enforces that the user is a community admin before the view can run
  """

  @wraps(function)
  def wrap(handler, request, *args, **kwargs):
    context: Context = request.context
    if context.user_is_logged_in and context.user_is_community_admin:
      return function(handler, request, *args, **kwargs)
    else:
      raise PermissionDenied

  wrap.__doc__ = function.__doc__
  wrap.__name__ = function.__name__
  return wrap

def super_admins_only(function):
  """
  This decorator enforces that a user is a super admin before the view can run
  """

  @wraps(function)
  def wrap(handler, request, *args, **kwargs):
    context: Context = request.context
    if context.user_is_logged_in and context.user_is_super_admin:
      return function(handler, request, *args, **kwargs)
    else:
      raise PermissionDenied

  wrap.__doc__ = function.__doc__
  wrap.__name__ = function.__name__
  return wrap

def cached_function(func):
  @wraps(func)
  def wrapper(handler, request, *args, **kwargs):
    subdomain = request.context.args.get('subdomain', None)

    if not subdomain:
      return CustomMassenergizeError("You are Missing a Required Input: subdomain")

    force_refresh = request.context.args.get('force_refresh', False)

    if force_refresh:
      cache.delete(f"{func.__module__}.{func.__name__}.{subdomain}")

    cache_key = f"{func.__module__}.{func.__name__}.{subdomain}"
    cached_data = cache.get(cache_key)

    if cached_data and not force_refresh:
      return cached_data
    else:
      result = func(handler, request, *args, **kwargs)
      cache.set(cache_key, result,)
      return result

  return wrapper
