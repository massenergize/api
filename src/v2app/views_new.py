from django.shortcuts import render
from django.http import JsonResponse
from database.utils.json_response_wrapper import Json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from database.utils.create_factory import CreateFactory
from database.utils.database_reader import DatabaseReader
from database.models import *
from database.utils.common import get_request_contents, rename_filter_args
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
def actions(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    actions, errors = FETCH.all(Action, args)
    return Json(actions, errors)
  elif request.method == 'POST':
    #about to create a new Action instance
    action, errors = FACTORY.create(Action, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def action(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    action, errors = FETCH.one(Action, args)
    return Json(action, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the Action resource with this <id>
    action, errors = FACTORY.update(Action, args)
    return Json(action, errors, use_full_json=True)
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
  return Json(None)



@csrf_exempt
def communities(request):
  args = get_request_contents(request)
  print(args)
  if request.method == 'GET':
    communities, errors = FETCH.all(Community, args)
    return Json(communities, errors)
  elif request.method == 'POST':
    #about to create a new Communitie instance
    communities, errors = FACTORY.create(Community, args)
    return Json(communities, errors)
  return Json(None)



@csrf_exempt
def community(request, cid):
  args = get_request_contents(request)
  args['id'] = cid
  if request.method == 'GET':
    community, errors = FETCH.one(Community, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    #TODO: create pages for this community, etc
    community, errors = FACTORY.update(Community, args)
    return Json(community, errors)
  return Json(None)


@csrf_exempt
def community_actions(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(Action, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_actions, errors = FACTORY.create(Action, args)
    return Json(community_actions, errors)
  return Json(None)



@csrf_exempt
def community_members(request, cid):
  args = get_request_contents(request)
  args['communities'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(UserProfile, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    member, errors = FACTORY.create(UserProfile, args)
    return Json(member, errors)
  return Json(None)



@csrf_exempt
def community_impact(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(Graph, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_impact, errors = FACTORY.create(Graph, args)
    return Json(community_impact, errors)
  return Json(None)



@csrf_exempt
def community_pages(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(Page, args)
    return Json(community, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_page, errors = FACTORY.create(Page, args)
    return Json(community_page, errors)
  return Json(None)



@csrf_exempt
def community_events(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(Event, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_event, errors = FACTORY.create(Event, args)
    return Json(community_event, errors)
  return Json(None)



@csrf_exempt
def community_households(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(RealEstateUnit, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_household, errors = FACTORY.create(RealEstateUnit, args)
    return Json(community_household, errors)
  return Json(None)



@csrf_exempt
def community_goals(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(Goal, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_goals, errors = FACTORY.create(Goal, args)
    return Json(community_goals, errors)
  return Json(None)



@csrf_exempt
def community_teams(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(Team, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_teams, errors = FACTORY.create(Community, args)
    return Json(community_teams, errors)
  return Json(None)



@csrf_exempt
def community_data(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
    community, errors = FETCH.all(Data, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community_data, errors = FACTORY.create(Community, args)
    return Json(community_data, errors)
  return Json(None)



@csrf_exempt
def community_testimonials(request, cid):
  args = get_request_contents(request)
  args['community'] = cid
  if request.method == 'GET':
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
def community_admin(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    communityadmin, errors = FETCH.one(CommunityAdminGroup, args)
    return Json(communityadmin, errors)
  elif request.method == 'POST':
    #updating the CommunityAdminGroup resource with this <id>
    communityadmin, errors = FACTORY.update(CommunityAdminGroup, args)
    return Json(communityadmin, errors)
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
  return Json(None)



@csrf_exempt
def pages(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    pages, errors = FETCH.all(Page, args)
    return Json(pages, errors, use_full_json=True)
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
    return Json(page, errors, use_full_json=True)
  elif request.method == 'POST':
    #updating the Page resource with this <id>
    page, errors = FACTORY.update(Page, args)
    return Json(page, errors)
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
  return Json(None)



@csrf_exempt
def user_households(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(RealEstateUnit, args)
    return Json(user, errors)
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
    print(args)
    user_action, errors = FACTORY.create(UserActionRel, args)
    return Json(user_action, errors)
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
    print(args)
    user_action, errors = FACTORY.update(UserActionRel, args)
    return Json(user_action, errors)
  return Json(None)



@csrf_exempt
def user_teams(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(Team, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user_team, errors = FACTORY.create(Team, args)
    return Json(user_team, errors)
  return Json(None)



@csrf_exempt
def user_testimonials(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user_testimonial, errors = FETCH.all(Testimonial, args)
    return Json(user_testimonial, errors)
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
  return Json(None)



@csrf_exempt
def vendors(request):
  args = get_request_contents(request)
  if request.method == 'GET':
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
  return Json(None)


@csrf_exempt
def new_uuid(request):
  return Json({'id': uuid.uuid4()})