"""
This file contains code to post data from the database.  This is meant to 
centralize the insertion of data into the database so that multiple apps can
call on the methods in this file without having to define their own
and to prevent code redundancy.
"""
from  ..models import *
from ..utils.common import ensure_required_fields
from ..utils.create_factory import CreateFactory


CREATE_ERROR_MSG = "An error occurred during creation.  Please check your \
    information and try again"

def create_one_object(model, fields, required_fields):
  pass


def create_multiple_objects(model, data_list):
  pass


def new_action(args):
  required_fields = ['title']
  errors = ensure_required_fields(required_fields, args)
  if errors:
    return {"success": False, "errors":errors}

  #if code gets here we have everything we need
  try:
    new_action = Action.objects.create()
    new_action.title = args["title"]
    new_action.save()
    return {"success": True, "action":new_action, "errors":None}
  except Exception as e:
    return {"success": False, "errors": [CREATE_ERROR_MSG, str(e)]}

def new_community(args):
  required_fields = ['name', 'domain']
  errors = ensure_required_fields(required_fields, args)
  if errors:
    return {"success": False, "errors":errors}

  #if code gets here we have everything we need
  try:
    new_action = Community.objects.create()
    return {"success": True, "new_action":new_action, "errors":None}
  except Exception as e:
    return {"success": False, "errors": [CREATE_ERROR_MSG, str(e)]}

def new_event(args):
  factory = CreateFactory(Event, args)
  return factory.create()



def new_user_profile(args):
  pass

def new_location(args):
  factory = CreateFactory(Location, args)
  return factory.create()


def new_subscriber(args):
  pass

def new_billing_statement(args):
  pass

def new_slider(args):
  pass 

def new_menu(args):
  pass 

def new_page_section(args):
  pass 

def new_page(args):
  pass

