"""
This file contains code to post data from the database.  This is meant to 
centralize the insertion of data into the database so that multiple apps can
call on the methods in this file without having to define their own
and to prevent code redundancy.
"""
from  ..models import *
from ..utils.common import ensure_required_fields
from ..utils.create_factory import CreateFactory


def new_action(args):
  factory = CreateFactory(Action, args)
  return factory.create(Action, args)

def new_community(args):
  factory = CreateFactory(Community, args)
  return factory.create()

def new_event(args):
  factory = CreateFactory(Event, args)
  return factory.create()


def new_user_profile(args):
  factory = CreateFactory(UserProfile, args)
  return factory.create(UserProfile, args)


def new_location(args):
  factory = CreateFactory(Location, args)
  return factory.create()


def new_subscriber(args):
  factory = CreateFactory(Subscriber, args)
  return factory.create(Subscriber, args)

def new_billing_statement(args):
  factory = CreateFactory(BillingStatement, args)
  return factory.create(BillingStatement, args)


def new_slider(args):
  factory = CreateFactory(Slider, args)
  return factory.create(Slider, args)


def new_menu(args):
  factory = CreateFactory(Menu, args)
  return factory.create(Menu, args)

def new_page_section(args):
  factory = CreateFactory(PageSection, args)
  return factory.create(PageSection, args)


def new_page(args):
  factory = CreateFactory(Page, args)
  return factory.create(Page, args)
