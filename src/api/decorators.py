"""
This contains custom decorators that can be used to check that specific 
conditions have been satisfied
"""
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from _main_.utils.context import Context
from functools import wraps
from _main_.utils.massenergize_errors import CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_logger import log
from django.core.cache import cache

def x_frame_options_exempt(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        response = view_func(*args, **kwargs)
        if isinstance(response, HttpResponse):
            response['X-Frame-Options'] = 'ALLOWALL'
        return response
    return wrapped_view


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
      log.exception(PermissionDenied)
      return NotAuthorizedError()

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
      log.exception(PermissionDenied)
      return NotAuthorizedError()

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
      log.exception(PermissionDenied)
      return NotAuthorizedError()
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
      log.exception(PermissionDenied)
      return NotAuthorizedError()

  wrap.__doc__ = function.__doc__
  wrap.__name__ = function.__name__
  return wrap

def cached_request(func):
    @wraps(func)
    def wrapper(handler, request, *args, **kwargs):
        context: Context = request.context
        args = context.args

        subdomain = args.get('subdomain', args.get("id", "None"))
        locale = context.preferred_language or 'en'

        force_refresh = context.args.get('force_refresh', False)

        if force_refresh:
            cache.delete(f"{func.__module__}.{func.__name__}.{subdomain}.{locale}")

        cache_key = f"{func.__module__}.{func.__name__}.{subdomain}.{locale}"
        cached_data = cache.get(cache_key)

        if cached_data and not force_refresh:
            return cached_data
        else:
            result = func(handler,request,**kwargs)
            cache.set(cache_key, result)
            return result

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__

    return wrapper