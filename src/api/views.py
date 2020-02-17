from django.shortcuts import render
from django.http import JsonResponse
from database.utils.json_response_wrapper import Json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from database.utils.create_factory import CreateFactory
from database.utils.database_reader import DatabaseReader
from database.models import *
from database.utils.common import get_request_contents, rename_filter_args
import requests
import os
import uuid


FACTORY = CreateFactory("Data Creator")
FETCH = DatabaseReader("Database Reader")

def ping(request):
	"""
	This view returns a dummy json.  It is meant to be used to check whether
	the server is alive or not
	"""
	return Json()


@csrf_exempt
def startup_data(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain 
  if request.method == 'GET':
    page = {}
    errors = {}
    pages, errors['pages'] = FETCH.all(Page, args)
    page['homePage'] = pages.filter(name = 'Home')[0]
    page['aboutUsPage'] = pages.filter(name = 'AboutUs')[0]
    page['donatePage'] = pages.filter(name = 'Donate')[0]
    # teamsPage = teams_stats() will just load this in if i need to when you visit that page the first time
    page['events'], errors['events'] = FETCH.all(Event, args)
    page['actions'], errors['actions'] = FETCH.all(Action, args)
    page['serviceProviders'], errors['serviceProviders'] = FETCH.all(Vendor, args)
    page['testimonials'], errors['testimonials'] = FETCH.all(Testimonial, args)
    page['communityData'], errors['communityData'] = FETCH.all(Data, args)
    page['community'], errors['community'] = FETCH.one(Community, args)

    args.pop('community__id', None)
    args.pop('community__subdomain', None)

    page['menus'], errors['menus'] = FETCH.all(Menu, args)
    page['policies'], errors['policies'] = FETCH.all(Policy, args)
    page['rsvps'], errors['rsvps'] = FETCH.all(EventAttendee, args)
    page['communities'], errors['communities'] = FETCH.all(Community, args)
    page['tagCols'], errors['tagCols'] = FETCH.all(TagCollection, args)
    return Json(page, errors)
  return Json(None)




@csrf_exempt
def actions(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    args['is_deleted'] = False
    actions, errors = FETCH.all(Action, args)
    return Json(actions, errors)
  elif request.method == 'POST':
    #about to create a new Action instance
    if 'tags' in args and isinstance(args['tags'], str):
      if args['tags'] != '':
        args['tags'] = [int(k) for k in args['tags'].split(',')]
      else:
        del args['tags']
    if 'vendors' in args and isinstance(args['vendors'], str):
      if  args['vendors'] != '':
        args['vendors'] = [int(k) for k in args['vendors'].split(',') if k != '']
      else:
        del args['vendors']
    if 'community' in args and isinstance(args['community'], str):
      args['community'] = int(args['community'])      
    if 'is_global' in args and isinstance(args['is_global'], str):
      args['is_global'] = args['is_global'] == 'true';   
    if 'image' in args and args['image']:
      img = args['image']
      media, errors = FACTORY.create(Media, {'file': img, 'media_type': "Image"})
      if media:
        media.save()
      if errors:
        print(errors)
      args['image'] = media.pk


    action, errors = FACTORY.create(Action, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def action(request, id):
  args = get_request_contents(request)
  args['id'] = int(id)
  if request.method == 'GET':
    action, errors = FETCH.one(Action, args)
    return Json(action, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the Action resource with this <id>
    if 'tags' in args and isinstance(args['tags'], str):
      args['tags'] = [int(k) for k in args['tags'].split(',')]
    if 'vendors' in args and isinstance(args['vendors'], str):
      args['vendors'] = [int(k) for k in args['vendors'].split(',') if k != '']
    if 'community' in args and isinstance(args['community'], str):
      args['community'] = int(args['community'])      
    if 'is_global' in args and isinstance(args['is_global'], str):
      args['is_global'] = args['is_global'] == 'true';   
      if args['is_global']:
        args['community'] = None
    
    if 'image' in args and args['image']:
      img = args['image']
      media, errors = FACTORY.create(Media, {'file': img})
      if media:
        media.save()
      if errors:
        print(errors)
        del args['image']
      else:
        args['image'] = media.pk
        
    action, errors = FACTORY.update(Action, args)
    # return JsonResponse({'success': True})
    return Json(action, errors, use_full_json=True)

  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Action, args)
    return Json(items_deleted, errors)
  return Json(None)


@csrf_exempt
def action_copy(request, id):
  """
  This is method will be used to handle the copying of an action
  """

  args = get_request_contents(request)
  args['id'] = int(id)
  action, errors = FETCH.one(Action, args)
  if action:
    action.pk = None
    action.title = str(action.title) +' Copy'
    action.save()
    return Json(action, errors)
  return Json()


@csrf_exempt
def action_testimonials(request, id):
  args = get_request_contents(request)
  args["action__id"] = id
  if request.method == 'GET':
    actions, errors = FETCH.all(Testimonial, args)
    return Json(actions, errors)
  elif request.method == 'POST':
    #about to create a new Action instance
    action, errors = FACTORY.create(Testimonial, args)
    return Json(action, errors)
  return Json(None)


@csrf_exempt
def action_properties(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    actionproperties, errors = FETCH.all(ActionProperty, args)
    return Json(actionproperties, errors)
  elif request.method == 'POST':
    #about to create a new ActionPropertie instance
    actionproperty, errors = FACTORY.create(ActionProperty, args)
    return Json(actionproperty, errors)
  return Json(None)



@csrf_exempt
def action_property(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    actionproperty, errors = FETCH.one(ActionProperty, args)
    return Json(actionproperty, errors)
  elif request.method == 'POST':
    #updating the ActionProperty resource with this <id>
    actionproperty, errors = FACTORY.update(ActionProperty, args)
    return Json(actionproperty, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(ActionProperty, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def billing_statements(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    billingstatements, errors = FETCH.all(BillingStatement, args)
    return Json(billingstatements, errors)
  elif request.method == 'POST':
    #about to create a new BillingStatement instance
    billingstatement, errors = FACTORY.create(BillingStatement, args)
    return Json(billingstatement, errors)
  return Json(None)



@csrf_exempt
def billing_statement(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    billingstatement, errors = FETCH.one(BillingStatement, args)
    return Json(billingstatement, errors)
  elif request.method == 'POST':
    #updating the BillingStatement resource with this <id>
    billingstatement, errors = FACTORY.update(BillingStatement, args)
    return Json(billingstatement, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(BillingStatement, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def communities(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    communities, errors = FETCH.all(Community, args)
    return Json(communities, errors)
  elif request.method == 'POST':
    #about to create a new Communitie instance
    communities, errors = FACTORY.create(Community, args)
    return Json(communities, errors)
  # elif request.method == 'DELETE':
  #   items_deleted, errors = FETCH.delete(Community, args)
  #   return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def community(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['id'] = cid
  if subdomain:
    args['subdomain'] = subdomain 
  if request.method == 'GET':
    community, errors = FETCH.one(Community, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    #TODO: create pages for this community, etc
    community, errors = FACTORY.update(Community, args)
    # print(community.simple_json())
    return Json(community, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Community, args)
    return Json(items_deleted, errors)
  return Json(None)


@csrf_exempt
def community_actions(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain 
  if request.method == 'GET':
    args['is_deleted'] = False
    community, errors = FETCH.all(Action, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_actions, errors = FACTORY.create(Action, args)
    return Json(community_actions, errors)
  return Json(None)



@csrf_exempt
def community_members(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['id'] = cid
  if subdomain:
    args['subdomain'] = subdomain 
  if request.method == 'GET':
    community, errors = FETCH.one(Community, args)
    if community:
      res = community.userprofile_set.all()
    return Json(res, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    member, errors = FACTORY.create(UserProfile, args)
    return Json(member, errors)
  return Json(None)



@csrf_exempt
def community_impact(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain  
  if request.method == 'GET':
    community, errors = FETCH.all(Graph, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_impact, errors = FACTORY.create(Graph, args)
    return Json(community_impact, errors)
  return Json(None)



@csrf_exempt
def community_pages(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain  
  if request.method == 'GET':
    community, errors = FETCH.all(Page, args)
    return Json(community, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_page, errors = FACTORY.create(Page, args)
    return Json(community_page, errors)
  return Json(None)



@csrf_exempt
def community_events(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain  
  if request.method == 'GET':
    args['is_deleted'] = False
    community, errors = FETCH.all(Event, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_event, errors = FACTORY.create(Event, args)
    return Json(community_event, errors)
  return Json(None)



@csrf_exempt
def community_households(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['id'] = cid
  if subdomain:
    args['subdomain'] = subdomain  
  if request.method == 'GET':
    community, errors = FETCH.one(Community, args)
    if community:
      res = community.userprofile_set.all()
      return Json(res, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_household, errors = FACTORY.create(RealEstateUnit, args)
    return Json(community_household, errors)
  return Json(None)



@csrf_exempt
def community_teams(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain  
  if request.method == 'GET':
    args['is_deleted'] = False
    community, errors = FETCH.all(Team, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_teams, errors = FACTORY.create(Community, args)
    return Json(community_teams, errors)
  return Json(None)



@csrf_exempt
def community_data(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain  
  if request.method == 'GET':
    community, errors = FETCH.all(Data, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_data, errors = FACTORY.create(Community, args)
    return Json(community_data, errors)
  return Json(None)



@csrf_exempt
def community_vendors(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['id'] = cid
  if subdomain:
    args['subdomain'] = subdomain 
  if request.method == 'GET':
    community, errors = FETCH.one(Community, args)
    if community:
      return Json(community.vendor_set.filter(is_deleted=False), errors)

  return Json(None)


@csrf_exempt
def community_testimonials(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['action__community__subdomain'] = subdomain 
  if request.method == 'GET':
    args['is_deleted'] = False
    community, errors = FETCH.all(Testimonial, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_testimonial, errors = FACTORY.create(Community, args)
    return Json(community_testimonial, errors)
  return Json(None)



@csrf_exempt
def community_admins(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    communityadmins, errors = FETCH.all(CommunityAdminGroup, args)
    return Json(communityadmins, errors)
  elif request.method == 'POST':
    #about to create a new CommunityAdmin instance
    communityadmin, errors = FACTORY.create(CommunityAdminGroup, args)
    return Json(communityadmin, errors)
  return Json(None)


@csrf_exempt
def community_admins_by_id_or_subdomain(request,cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain 
  if request.method == 'GET':
    communityadmins, errors = FETCH.all(CommunityAdminGroup, args)
    return Json(communityadmins, errors)
  elif request.method == 'POST':
    #about to create a new CommunityAdmin instance
    communityadmin, errors = FACTORY.create(CommunityAdminGroup, args)
    return Json(communityadmin, errors)
  return Json(None)



@csrf_exempt
def community_admin_group(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    communityadmin, errors = FETCH.one(CommunityAdminGroup, args)
    return Json(communityadmin, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the CommunityAdminGroup resource with this <id>
    communityadmin, errors = FACTORY.update(CommunityAdminGroup, args)
    return Json(communityadmin, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(CommunityAdminGroup, args)
    return Json(items_deleted, errors)
  return Json(None)

def community_profile_full(request, cid):
  args = get_request_contents(request)
  args['id'] = cid
  if request.method == 'GET':
    community, errors = FETCH.one(Community, args)
    if community:
      res = community.full_json()
      res['users'] = [u.simple_json() for u in community.userprofile_set.all()]
      res['testimonials'] = [t.simple_json() for t in community.testimonial_set.all()[:3]]
      res['events'] = [e.simple_json() for e in community.event_set.all()[:3]]
      res['actions'] = [a.simple_json() for a in community.action_set.all()[:3]]
      res['graphs'] = [g.simple_json() for g in community.graph_set.all()]
      return Json(res, errors, use_full_json=True)
  return Json(None)


@csrf_exempt
def email_categories(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    emailcategories, errors = FETCH.all(EmailCategory, args)
    return Json(emailcategories, errors)
  elif request.method == 'POST':
    #about to create a new EmailCategory instance
    emailcategory, errors = FACTORY.create(EmailCategory, args)
    return Json(emailcategory, errors)
  return Json(None)



@csrf_exempt
def email_category(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    emailcategory, errors = FETCH.one(EmailCategory, args)
    return Json(emailcategory, errors)
  elif request.method == 'POST':
    #updating the EmailCategory resource with this <id>
    emailcategory, errors = FACTORY.update(EmailCategory, args)
    return Json(emailcategory, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(EmailCategory, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def events(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    events, errors = FETCH.all(Event, args)
    return Json(events, errors)
  elif request.method == 'POST':
    #about to create a new Event instance
    event, errors = FACTORY.create(Event, args)
    return Json(event, errors)
  return Json(None)



@csrf_exempt
def event(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    event, errors = FETCH.one(Event, args)
    return Json(event, errors)
  elif request.method == 'POST':
    #updating the Event resource with this <id>
    event, errors = FACTORY.update(Event, args)
    return Json(event, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Event, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def event_attendees(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    eventattendees, errors = FETCH.all(EventAttendee, args)
    return Json(eventattendees, errors)
  elif request.method == 'POST':
    #about to create a new EventAttendee instance
    eventattendee, errors = FACTORY.create(EventAttendee, args)
    return Json(eventattendee, errors)
  return Json(None)



@csrf_exempt
def event_attendee(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    eventattendee, errors = FETCH.one(EventAttendee, args)
    return Json(eventattendee, errors)
  elif request.method == 'POST':
    #updating the EventAttendee resource with this <id>
    eventattendee, errors = FACTORY.update(EventAttendee, args)
    return Json(eventattendee, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(EventAttendee, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def goals(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    goals, errors = FETCH.all(Goal, args)
    return Json(goals, errors)
  elif request.method == 'POST':
    #about to create a new Goal instance
    goal, errors = FACTORY.create(Goal, args)
    return Json(goal, errors)
  return Json(None)



@csrf_exempt
def goal(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    goal, errors = FETCH.one(Goal, args)
    return Json(goal, errors)
  elif request.method == 'POST':
    #updating the Goal resource with this <id>
    goal, errors = FACTORY.update(Goal, args)
    return Json(goal, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Goal, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def graphs(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    graphs, errors = FETCH.all(Graph, args)
    return Json(graphs, errors)
  elif request.method == 'POST':
    #about to create a new Graph instance
    graph, errors = FACTORY.create(Graph, args)
    return Json(graph, errors)
  return Json(None)



@csrf_exempt
def graph(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    graph, errors = FETCH.one(Graph, args)
    return Json(graph, errors)
  elif request.method == 'POST':
    #updating the Graph resource with this <id>
    graph, errors = FACTORY.update(Graph, args)
    return Json(graph, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Graph, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def households(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    households, errors = FETCH.all(RealEstateUnit, args)
    return Json(households, errors)
  elif request.method == 'POST':
    #about to create a new Household instance
    household, errors = FACTORY.create(RealEstateUnit, args)
    return Json(household, errors)
  return Json(None)



@csrf_exempt
def household(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    household, errors = FETCH.one(RealEstateUnit, args)
    return Json(household, errors)
  elif request.method == 'POST':
    #updating the Household resource with this <id>
    household, errors = FACTORY.update(RealEstateUnit, args)
    return Json(household, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(RealEstateUnit, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def locations(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    locations, errors = FETCH.all(Location, args)
    return Json(locations, errors)
  elif request.method == 'POST':
    #about to create a new Location instance
    location, errors = FACTORY.create(Location, args)
    return Json(location, errors)
  return Json(None)



@csrf_exempt
def location(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    location, errors = FETCH.one(Location, args)
    return Json(location, errors)
  elif request.method == 'POST':
    #updating the Location resource with this <id>
    location, errors = FACTORY.update(Location, args)
    return Json(location, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Location, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def media(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    medias, errors = FETCH.all(Media, args)
    return Json(medias, errors)
  elif request.method == 'POST':
    #about to create a new Media instance
    media, errors = FACTORY.create(Media, args)
    return Json(media, errors)
  return Json(None)



@csrf_exempt
def media_by_id(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    media, errors = FETCH.one(Media, args)
    return Json(media, errors)
  elif request.method == 'POST':
    #updating the Media resource with this <id>
    media, errors = FACTORY.update(Media, args)
    return Json(media, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Media, args)
    return Json(items_deleted, errors)
  return Json(None)


@csrf_exempt
def media_with_slug(request, slug):
  args = get_request_contents(request)
  args['name'] = slug
  if request.method == 'GET':
    media, errors = FETCH.one(Media, args)
    return Json(media, errors)
  elif request.method == 'POST':
    #updating the Media resource with this <id>
    media, errors = FACTORY.update(Media, args)
    return Json(media, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Media, args)
    return Json(items_deleted, errors)
  return Json(None)

@csrf_exempt
def menus(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    menus, errors = FETCH.all(Menu, args)
    return Json(menus, errors)
  elif request.method == 'POST':
    #about to create a new Menu instance
    menu, errors = FACTORY.create(Menu, args)
    return Json(menu, errors)
  return Json(None)



@csrf_exempt
def menu(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    menu, errors = FETCH.one(Menu, args)
    return Json(menu, errors)
  elif request.method == 'POST':
    #updating the Menu resource with this <id>
    menu, errors = FACTORY.update(Menu, args)
    return Json(menu, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Menu, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def pages(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    pages, errors = FETCH.all(Page, args)
    if len(pages) == 1:
      return Json(pages, errors, use_full_json=True)
    else:
      return Json(pages, errors)
  elif request.method == 'POST':
    #about to create a new Page instance
    page, errors = FACTORY.create(Page, args)
    return Json(page, errors)
  return Json(None)



@csrf_exempt
def page(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    page, errors = FETCH.one(Page, args)
    return Json(page, errors)
  elif request.method == 'POST':
    #updating the Page resource with this <id>
    page, errors = FACTORY.update(Page, args)
    return Json(page, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Page, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def page_sections(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    pagesections, errors = FETCH.all(PageSection, args)
    return Json(pagesections, errors)
  elif request.method == 'POST':
    #about to create a new PageSection instance
    pagesection, errors = FACTORY.create(PageSection, args)
    return Json(pagesection, errors)
  return Json(None)



@csrf_exempt
def page_section(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    pagesection, errors = FETCH.one(PageSection, args)
    return Json(pagesection, errors)
  elif request.method == 'POST':
    #updating the PageSection resource with this <id>
    pagesection, errors = FACTORY.update(PageSection, args)
    return Json(pagesection, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(PageSection, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def permissions(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    permissions, errors = FETCH.all(Permission, args)
    return Json(permissions, errors)
  elif request.method == 'POST':
    #about to create a new Permission instance
    permission, errors = FACTORY.create(Permission, args)
    return Json(permission, errors)
  return Json(None)



@csrf_exempt
def permission(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    permission, errors = FETCH.one(Permission, args)
    return Json(permission, errors)
  elif request.method == 'POST':
    #updating the Permission resource with this <id>
    permission, errors = FACTORY.update(Permission, args)
    return Json(permission, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Permission, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def policies(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    policies, errors = FETCH.all(Policy, args)
    return Json(policies, errors)
  elif request.method == 'POST':
    #about to create a new Policy instance
    policy, errors = FACTORY.create(Policy, args)
    return Json(policy, errors)
  return Json(None)



@csrf_exempt
def policy(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    policies, errors = FETCH.one(Policy, args)
    return Json(policies, errors)
  elif request.method == 'POST':
    #updating the Policy resource with this <id>
    policy, errors = FACTORY.update(Policy, args)
    return Json(policy, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Policy, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def roles(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    roles, errors = FETCH.all(Role, args)
    return Json(roles, errors)
  elif request.method == 'POST':
    #about to create a new Role instance
    role, errors = FACTORY.create(Role, args)
    return Json(role, errors)
  return Json(None)



@csrf_exempt
def role(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    role, errors = FETCH.one(Role, args)
    return Json(role, errors)
  elif request.method == 'POST':
    #updating the Role resource with this <id>
    role, errors = FACTORY.update(Role, args)
    return Json(role, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Role, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def services(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    services, errors = FETCH.all(Service, args)
    return Json(services, errors)
  elif request.method == 'POST':
    #about to create a new Service instance
    service, errors = FACTORY.create(Service, args)
    return Json(service, errors)
  return Json(None)



@csrf_exempt
def service(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    service, errors = FETCH.one(Service, args)
    return Json(service, errors)
  elif request.method == 'POST':
    #updating the Service resource with this <id>
    service, errors = FACTORY.update(Service, args)
    return Json(service, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Service, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def sliders(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    sliders, errors = FETCH.all(Slider, args)
    return Json(sliders, errors)
  elif request.method == 'POST':
    #about to create a new Slider instance
    slider, errors = FACTORY.create(Slider, args)
    return Json(slider, errors)
  return Json(None)



@csrf_exempt
def slider(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    sliders, errors = FETCH.one(Slider, args)
    return Json(sliders, errors)
  elif request.method == 'POST':
    #updating the Slider resource with this <id>
    slider, errors = FACTORY.update(Slider, args)
    return Json(slider, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Slider, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def slider_images(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    sliderimages, errors = FETCH.all(SliderImage, args)
    return Json(sliderimages, errors)
  elif request.method == 'POST':
    #about to create a new SliderImage instance
    sliderimage, errors = FACTORY.create(SliderImage, args)
    return Json(sliderimage, errors)
  return Json(None)



@csrf_exempt
def slider_image(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    sliderimage, errors = FETCH.one(SliderImage, args)
    return Json(sliderimage, errors)
  elif request.method == 'POST':
    #updating the SliderImage resource with this <id>
    sliderimage, errors = FACTORY.update(SliderImage, args)
    return Json(sliderimage, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(SliderImage, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def data(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    statistics, errors = FETCH.all(Data, args)
    return Json(statistics, errors)
  elif request.method == 'POST':
    #about to create a new Data instance
    data, errors = FACTORY.create(Data, args)
    return Json(data, errors)
  return Json(None)



@csrf_exempt
def data_by_id(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    data, errors = FETCH.all(Data, args)
    return Json(data, errors)
  elif request.method == 'POST':
    #updating the Data resource with this <id>
    data, errors = FACTORY.update(Data, args)
    return Json(data, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Data, args)
    return Json(items_deleted, errors)
  return Json(None)


@csrf_exempt
def subscribers(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    subscribers, errors = FETCH.all(Subscriber, args)
    return Json(subscribers, errors)
  elif request.method == 'POST':
    #about to create a new Subscriber instance
    subscriber, errors = FACTORY.create(Subscriber, args)
    return Json(subscriber, errors)
  return Json(None)



@csrf_exempt
def subscriber(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    subscriber, errors = FETCH.all(Subscriber, args)
    return Json(subscriber, errors)
  elif request.method == 'POST':
    #updating the Subscriber resource with this <id>
    subscriber, errors = FACTORY.update(Subscriber, args)
    return Json(subscriber, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Subscriber, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def subscriber_email_preferences(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    preferences, errors = FETCH.all(SubscriberEmailPreference, args)
    return Json(preferences, errors)
  elif request.method == 'POST':
    #about to create a new SubscriberEmailPreference instance
    pref, errors = FACTORY.create(SubscriberEmailPreference, args)
    return Json(pref, errors)
  return Json(None)



@csrf_exempt
def subscriber_email_preference(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    pref, errors = FETCH.one(SubscriberEmailPreference, args)
    return Json(pref, errors)
  elif request.method == 'POST':
    #updating the SubscriberEmailPreference resource with this <id>
    pref, errors = FACTORY.update(SubscriberEmailPreference, args)
    return Json(pref, errors)
  return Json(None)



# @csrf_exempt
def tags(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    tags, errors = FETCH.all(Tag, args)
    return Json(tags, errors)
  elif request.method == 'POST':
    #about to create a new Tag instance
    tag, errors = FACTORY.create(Tag, args)
    return Json(tag, errors)
  return Json(None)



@csrf_exempt
def tag(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    tag, errors = FETCH.one(Tag, args)
    return Json(tag, errors)
  elif request.method == 'POST':
    #updating the Tag resource with this <id>
    tag, errors = FACTORY.update(Tag, args)
    return Json(tag, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Tag, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def tag_collections(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    tagcollections, errors = FETCH.all(TagCollection, args)
    return Json(tagcollections, errors)
  elif request.method == 'POST':
    #about to create a new TagCollection instance
    tagcollection, errors = FACTORY.create(TagCollection, args)
    return Json(tagcollection, errors)
  return Json(None)



@csrf_exempt
def tag_collection(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    tagcollection, errors = FETCH.one(TagCollection, args)
    return Json(tagcollection, errors)
  elif request.method == 'POST':
    #updating the TagCollection resource with this <id>
    tagcollection, errors = FACTORY.update(TagCollection, args)
    return Json(tagcollection, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(TagCollection, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def teams(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    teams, errors = FETCH.all(Team, args)
    return Json(teams, errors)
  elif request.method == 'POST':
    #about to create a new Team instance
    team, errors = FACTORY.create(Team, args)
    return Json(team, errors)
  return Json(None)



@csrf_exempt
def team(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    team, errors = FETCH.one(Team, args)
    return Json(team, errors)
  elif request.method == 'POST':
    #updating the Team resource with this <id>
    team, errors = FACTORY.update(Team, args)
    return Json(team, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Team, args)
    return Json(items_deleted, errors)
  return Json(None)


@csrf_exempt
def team_member(request, team_id, member_id):
  if request.method == 'DELETE':
    team, errors = FETCH.get_one(Team, {'id': team_id})
    team_member, errors = FETCH.get_one(UserProfile, {'id': member_id})
    if(team and team_member):
      teamMember = TeamMember.objects.filter(team=team,user=team_member)
      teamMember.delete()
      # team.members being deprecated.  Does this call get used?
      print("views/team_member")
      #team.members.remove(team_member)
      #team.save()
      return Json(team, errors)
  return Json(None)


@csrf_exempt
def team_stats(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    team, errors = FETCH.one(Team, args)
    if team:
      res = {"households": 0, "actions": 0, "actions_completed": 0, "actions_todo": 0}
      res["team"] = team.simple_json()
      #Team.member deprecated
      #for m in team.members.all():
      teamMembers = TeamMember.objects.filter(team=team)
      res["members"] = teamMembers.count()
      for m in teamMembers:
        user = m.user
        res["households"] += len(user.real_estate_units.all())
        actions = user.useractionrel_set.all()
        res["actions"] += len(actions)
        res["actions_completed"] += len(actions.filter(**{"status":"DONE"}))
        res["actions_todo"] += len(actions.filter(**{"status":"TODO"}))
      return Json(res, errors)

  return Json(None)


@csrf_exempt
def teams_stats(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    teams, errors = FETCH.all(Team, args)
    ans = []
    for team in teams:
      res = {"households": 0, "actions": 0, "actions_completed": 0, "actions_todo": 0}
      res["team"] = team.simple_json()
      #Team.member deprecated
      #for m in team.members.all():
      teamMembers = TeamMember.objects.filter(team=team)
      res["members"] = teamMembers.count()
      for m in teamMembers:
        res["households"] += len(user.real_estate_units.all())
        actions = user.useractionrel_set.all()
        res["actions"] += len(actions)
        res["actions_completed"] += len(actions.filter(**{"status":"DONE"}))
        res["actions_todo"] += len(actions.filter(**{"status":"TODO"}))
      ans.append(res)
    return Json(ans, errors,do_not_serialize=True)

  return Json(None)

@csrf_exempt
def communities_stats(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    communities, errors = FETCH.all(Community, args)
    ans = []
    for community in communities:
      res = {"households_engaged": 0, "actions_completed": 0, "users_engaged":0}
      res["community"] = community.simple_json()
      users, errors = FETCH.all(UserProfile, {"communities": community.id})
      res["users_engaged"] = len(users)

      # changed to fix graph inconsistencies
      communityData = community.full_json()
      communityGoal = communityData["goal"]
      res["households_engaged"] = communityGoal["attained_number_of_households"]
      res["actions_completed"] = communityGoal["attained_number_of_actions"]
    
      ans.append(res)
  return Json(ans, errors, do_not_serialize=True)

@csrf_exempt
def community_stats(request, cid):
  args = get_request_contents(request)
  args["id"] = cid
  if request.method == 'GET':
    community, errors = FETCH.one(Community, args)
    if community:
      res = {"households_engaged": 0, "actions_completed": 0, "users_engaged":0}
      res["community"] = community.simple_json();
      users, errors = FETCH.all(UserProfile, {"communities": community.id})
      res["users_engaged"] = len(users);

      # changed to fix graph inconsistencies
      communityData = community.full_json()
      communityGoal = communityData["goal"]
      res["households_engaged"] = communityGoal["attained_number_of_households"]
      res["actions_completed"] = communityGoal["attained_number_of_actions"]

      return Json(res, errors, do_not_serialize=True)
  return Json(None)

@csrf_exempt
def testimonials(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    testimonials, errors = FETCH.all(Testimonial, args)
    return Json(testimonials, errors)
  elif request.method == 'POST':
    #about to create a new Testimonial instance
    testimonial, errors = FACTORY.create(Testimonial, args)
    return Json(testimonial, errors)
  return Json(None)



@csrf_exempt
def testimonial(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    testimonial, errors = FETCH.one(Testimonial, args)
    return Json(testimonial, errors)
  elif request.method == 'POST':
    #updating the Testimonial resource with this <id>
    testimonial, errors = FACTORY.update(Testimonial, args)
    return Json(testimonial, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Testimonial, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def users(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    users, errors = FETCH.all(UserProfile, args)
    return Json(users, errors)
  elif request.method == 'POST':
    #about to create a new User instance
    user, errors = FACTORY.create(UserProfile, args)
    return Json(user, errors)
  return Json(None)



@csrf_exempt
def user(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.one(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.update(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(UserProfile, args)
    return Json(items_deleted, errors)
  return Json(None)


@csrf_exempt
def user_by_email(request, email):
  args = get_request_contents(request)
  args['email'] = email
  if request.method == 'GET':
    user, errors = FETCH.one(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.update(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(UserProfile, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def user_households(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args, 
      many_to_many_fields_to_prefetch=['real_estate_units'])
    if user:
      households = user.first().real_estate_units.all()
    return Json(households, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(RealEstateUnit, args)
    return Json(user, errors)
  return Json(None)


@csrf_exempt
def user_households_by_email(request, email):
  #TODO: not working yet
  args = get_request_contents(request)
  args['email'] = email
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args, 
      many_to_many_fields_to_prefetch=['real_estate_units'])
    if user:
      households = user.first().real_estate_units.all()
    return Json(households, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(RealEstateUnit, args)
    return Json(user, errors)
  return Json(None)



@csrf_exempt
def user_household_actions(request, id, hid):
  args = get_request_contents(request)
  args['id'] = id
  args['real_estate_unit'] = hid
  if request.method == 'GET':
    user_households, errors = FETCH.all(Action, args)
    return Json(user_households, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(Action, args)
    return Json(user, errors)
  return Json(None)


@csrf_exempt
def user_household_actions_by_email(request, email, hid):
  args = get_request_contents(request)
  args['email'] = email
  args['real_estate_unit'] = hid
  if request.method == 'GET':
    user, errors = FETCH.all(Action, args)
    return Json(user, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(Action, args)
    return Json(user, errors)
  return Json(None)



@csrf_exempt
def user_actions(request, id):
  args = get_request_contents(request)
  args['user'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(UserActionRel, args)
    return Json(user, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_action, errors = FACTORY.create(UserActionRel, args)
    return Json(user_action, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(UserActionRel, args)
    return Json(items_deleted, errors)
  return Json(None)


@csrf_exempt
def user_actions_by_email(request, email):
  args = get_request_contents(request)
  args['user__email'] = email
  if request.method == 'GET':
    user, errors = FETCH.all(UserActionRel, args)
    return Json(user, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_action, errors = FACTORY.create(UserActionRel, args)
    return Json(user_action, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(UserActionRel, args)
    return Json(items_deleted, errors)
  return Json(None)

@csrf_exempt
def user_action(request, id, aid):
  args = get_request_contents(request)
  args['user'] = id
  args['id'] = aid
  if request.method == 'GET':
    user, errors = FETCH.one(UserActionRel, args)
    return Json(user, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_action, errors = FACTORY.update(UserActionRel, args)
    return Json(user_action, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(UserActionRel, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def user_action_by_email(request, email, aid):
  args = get_request_contents(request)
  args['user__email'] = email
  args['id'] = aid
  if request.method == 'GET':
    user, errors = FETCH.one(UserActionRel, args)
    return Json(user, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_action, errors = FACTORY.update(UserActionRel, args)
    return Json(user_action, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(UserActionRel, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def user_teams(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args)
    if user:
      user = user.first()
      return Json(user.team_members.all(), errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_team, errors = FACTORY.create(Team, args)
    return Json(user_team, errors)
  return Json(None)


@csrf_exempt
def user_teams_by_email(request, email):
  args = get_request_contents(request)
  args['email'] = email
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args)
    if user:
      user = user.first()
      return Json(user.team_members.all(), errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_team, errors = FACTORY.create(Team, args)
    return Json(user_team, errors)
  return Json(None)



@csrf_exempt
def user_testimonials(request, id):
  args = get_request_contents(request)
  args['user__id'] = id
  if request.method == 'GET':
    user_testimonials, errors = FETCH.all(Testimonial, args)
    return Json(user_testimonials, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_testimonial, errors = FACTORY.create(Testimonial, args)
    return Json(user_testimonial, errors)
  return Json(None)


@csrf_exempt
def user_testimonials_by_email(request, email):
  args = get_request_contents(request)
  args['user__email'] = email
  if request.method == 'GET':
    user_testimonials, errors = FETCH.all(Testimonial, args)
    return Json(user_testimonials, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_testimonial, errors = FACTORY.create(Testimonial, args)
    return Json(user_testimonial, errors)
  return Json(None)


@csrf_exempt
def user_groups(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    usergroups, errors = FETCH.all(UserGroup, args)
    return Json(UserGroup, errors)
  elif request.method == 'POST':
    #about to create a new UserGroup instance
    usergroup, errors = FACTORY.create(UserGroup, args)
    return Json(usergroup, errors)
  return Json(None)



@csrf_exempt
def user_group(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    usergroup, errors = FETCH.one(UserGroup, args)
    return Json(usergroup, errors)
  elif request.method == 'POST':
    #updating the UserGroup resource with this <id>
    usergroup, errors = FACTORY.update(UserGroup, args)
    return Json(usergroup, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(UserGroup, args)
    return Json(items_deleted, errors)
  return Json(None)


@csrf_exempt
def user_group_by_email(request, email):
  args = get_request_contents(request)
  args['email'] = email
  if request.method == 'GET':
    usergroup, errors = FETCH.one(UserGroup, args)
    return Json(usergroup, errors)
  elif request.method == 'POST':
    #updating the UserGroup resource with this <id>
    usergroup, errors = FACTORY.update(UserGroup, args)
    return Json(usergroup, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(UserGroup, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def vendors(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    args['is_deleted'] = False
    vendors, errors = FETCH.all(Vendor, args)
    return Json(vendors, errors)
  elif request.method == 'POST':
    #about to create a new Vendor instance
    vendor, errors = FACTORY.create(Vendor, args)
    return Json(vendor, errors)
  return Json(None)



@csrf_exempt
def vendor(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    vendor, errors = FETCH.one(Vendor, args)
    return Json(vendor, errors)
  elif request.method == 'POST':
    #updating the Vendor resource with this <id>
    vendor, errors = FACTORY.update(Vendor, args)
    return Json(vendor, errors)
  elif request.method == 'DELETE':
    items_deleted, errors = FETCH.delete(Vendor, args)
    return Json(items_deleted, errors)
  return Json(None)



@csrf_exempt
def startup_data(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['id'] = cid
  if subdomain:
    args['subdomain'] = subdomain 
  if request.method == 'GET':
    c, err = FETCH.one(Community, args)
    result = { 
      'community': c.simple_json(),
      'pages' : [p.full_json() for p in c.page_set.all()],
      'events' : [e.full_json() for e in c.event_set.all()],
      'actions' : [a.simple_json() for a in c.action_set.all()],
      'service_providers' : [e.full_json() for e in FETCH.all(Vendor, {})[0]],
      'testimonials' :[e.full_json() for e in c.testimonial_set.all()],
      'communityData': [e.full_json() for e in c.data_set.all()],
    }
    args = {'community__subdomain': subdomain}
    menu, err = FETCH.all(Menu, {})
    policies, err = FETCH.all(Policy, {})
    rsvps, err = FETCH.all(EventAttendee, args)
    communities, err = FETCH.all(Community, {})
    tag_collections, err = FETCH.all(TagCollection, {})
    result['menu'] = [m.simple_json() for m in menu]
    result['policies'] = [p.simple_json() for p in policies]
    # result['rsvps'] = [r.simple_json() for r in rsvps]
    result['communities'] = [c.simple_json() for c in communities]
    result['tag_collections'] = [t.full_json() for t in tag_collections]
    return Json(result)
  return Json(None)

@csrf_exempt
def verify_captcha(request):
  args = get_request_contents(request)
  if 'captchaString' in args:
    data = {
      'secret': os.environ.get('RECAPTCHA_SECRET_KEY'),
      'response': args['captchaString']
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    if result['success']:
      return(Json(result))
    else:
      return Json(None, ['Invalid reCAPTCHA. Please try again.'])
  return Json(None, ['You are missing required field: "captchaString"'])


def home_page(request, cid=None, subdomain=None):
  args = get_request_contents(request)
  if cid:
    args['community__id'] = cid
  if subdomain:
    args['community__subdomain'] = subdomain 
  args['name'] = 'Home'
  
  if request.method == 'GET':
    home_page, err = FACTORY.create(Page, args)
    if err:
      return Json(None, err)
    
  elif request.method== 'POST':
    c, err = FETCH.one(Page, args)
  return Json(None)