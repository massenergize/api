from django.shortcuts import render
from django.http import JsonResponse
from database.CRUD import create, read as fetch
from database.utils.json_response_wrapper import Json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from database.utils.create_factory import CreateFactory
from database.utils.database_reader import DatabaseReader
from  database.models import *
from database.utils.common import get_request_contents, rename_filter_args

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
  if request.method == "GET":
    actions, errors = FETCH.all(Action, args)
    return Json(actions, errors)
  elif request.method == "POST":
    action, errors = FACTORY.create(Action, args)
    return Json(action, errors)
  return Json()


@csrf_exempt
def action(request, id):
  args = get_request_contents(request)
  if request.method == "GET":
    action, errors = FETCH.one(Action, args)
    return Json(action, errors)
  elif request.method == "POST":
    #this means they want to update the action resource with this <id>
    action, errors = FACTORY.update(Action, args)
    return Json(action, errors)
  return Json()



@csrf_exempt
def actions(request):
  args = get_request_contents(request)
  if request.method == "GET":
    actions, errors = FETCH.all(Action, args)
    return Json(actions, errors)
  elif request.method == "POST":
    action, errors = FACTORY.create(Action, args)
    return Json(action, errors)
  return Json()


@csrf_exempt
def action(request, id):
  args = get_request_contents(request)
  if request.method == "GET":
    action, errors = FETCH.one(Action, args)
    return Json(action, errors)
  elif request.method == "POST":
    #this means they want to update the action resource with this <id>
    action, errors = FACTORY.update(Action, args)
    return Json(action, errors)
  return Json()



@csrf_exempt
def actions(request):
  args = get_request_contents(request)
  if request.method == "GET":
    actions, errors = FETCH.all(Action, args)
    return Json(actions, errors)
  elif request.method == "POST":
    action, errors = FACTORY.create(Action, args)
    return Json(action, errors)
  return Json()


@csrf_exempt
def action(request, id):
  args = get_request_contents(request)
  if request.method == "GET":
    action, errors = FETCH.one(Action, args)
    return Json(action, errors)
  elif request.method == "POST":
    #this means they want to update the action resource with this <id>
    action, errors = FACTORY.update(Action, args)
    return Json(action, errors)
  return Json()


@csrf_exempt
def actions(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    actions, errors = FETCH.all(Action, args)
    return Json(Action, errors)
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
    action, errors = FETCH.all(Action, args)
    return Json(action, errors)
  elif request.method == 'POST':
    #updating the Action resource with this <id>
    action, errors = FACTORY.create(Action, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def action_properties(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    actionproperties, errors = FETCH.all(ActionProperty, args)
    return Json(ActionProperty, errors)
  elif request.method == 'POST':
    #about to create a new ActionPropertie instance
    actionpropertie, errors = FACTORY.create(ActionProperty, args)
    return Json(actionpropertie, errors)
  return Json(None)



@csrf_exempt
def action_property(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    actionproperty, errors = FETCH.all(ActionProperty, args)
    return Json(actionproperty, errors)
  elif request.method == 'POST':
    #updating the ActionProperty resource with this <id>
    actionproperty, errors = FACTORY.create(ActionProperty, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def billing_statements(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    billingstatements, errors = FETCH.all(BillingStatement, args)
    return Json(BillingStatement, errors)
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
    billingstatement, errors = FETCH.all(BillingStatement, args)
    return Json(billingstatement, errors)
  elif request.method == 'POST':
    #updating the BillingStatement resource with this <id>
    billingstatement, errors = FACTORY.create(BillingStatement, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def communities(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    communities, errors = FETCH.all(Community, args)
    return Json(Community, errors)
  elif request.method == 'POST':
    #about to create a new Communitie instance
    communities, errors = FACTORY.create(Community, args)
    return Json(communities, errors)
  return Json(None)



@csrf_exempt
def community(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    community, errors = FETCH.all(Community, args)
    return Json(community, errors)
  elif request.method == 'POST':
    #updating the Community resource with this <id>
    community, errors = FACTORY.create(Community, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def community_admins(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    communityadmins, errors = FETCH.all(CommunityAdminGroup, args)
    return Json(CommunityAdminGroup, errors)
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
    communityadmin, errors = FETCH.all(CommunityAdminGroup, args)
    return Json(communityadmin, errors)
  elif request.method == 'POST':
    #updating the CommunityAdminGroup resource with this <id>
    communityadmin, errors = FACTORY.create(CommunityAdminGroup, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def email_categories(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    emailcategories, errors = FETCH.all(EmailCategory, args)
    return Json(EmailCategory, errors)
  elif request.method == 'POST':
    #about to create a new EmailCategorie instance
    emailcategory, errors = FACTORY.create(EmailCategory, args)
    return Json(emailcategory, errors)
  return Json(None)



@csrf_exempt
def email_category(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    emailcategory, errors = FETCH.all(EmailCategory, args)
    return Json(emailcategory, errors)
  elif request.method == 'POST':
    #updating the EmailCategory resource with this <id>
    emailcategory, errors = FACTORY.create(EmailCategory, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def events(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    events, errors = FETCH.all(Event, args)
    return Json(Event, errors)
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
    event, errors = FETCH.all(Event, args)
    return Json(event, errors)
  elif request.method == 'POST':
    #updating the Event resource with this <id>
    event, errors = FACTORY.create(Event, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def event_attendees(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    eventattendees, errors = FETCH.all(EventAttendees, args)
    return Json(EventAttendees, errors)
  elif request.method == 'POST':
    #about to create a new EventAttendee instance
    eventattendee, errors = FACTORY.create(EventAttendees, args)
    return Json(eventattendee, errors)
  return Json(None)



@csrf_exempt
def event_attendee(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    eventattendee, errors = FETCH.all(EventAttendees, args)
    return Json(eventattendee, errors)
  elif request.method == 'POST':
    #updating the EventAttendee resource with this <id>
    eventattendee, errors = FACTORY.create(EventAttendees, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def goals(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    goals, errors = FETCH.all(Goal, args)
    return Json(Goal, errors)
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
    goal, errors = FETCH.all(Goal, args)
    return Json(goal, errors)
  elif request.method == 'POST':
    #updating the Goal resource with this <id>
    goal, errors = FACTORY.create(Goal, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def graphs(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    graphs, errors = FETCH.all(Graph, args)
    return Json(Graph, errors)
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
    graph, errors = FETCH.all(Graph, args)
    return Json(graph, errors)
  elif request.method == 'POST':
    #updating the Graph resource with this <id>
    graph, errors = FACTORY.create(Graph, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def households(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    households, errors = FETCH.all(RealEstateUnit, args)
    return Json(RealEstateUnit, errors)
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
    household, errors = FETCH.all(RealEstateUnit, args)
    return Json(household, errors)
  elif request.method == 'POST':
    #updating the Household resource with this <id>
    household, errors = FACTORY.create(RealEstateUnit, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def locations(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    locations, errors = FETCH.all(Location, args)
    return Json(Location, errors)
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
    location, errors = FETCH.all(Location, args)
    return Json(location, errors)
  elif request.method == 'POST':
    #updating the Location resource with this <id>
    location, errors = FACTORY.create(Location, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def media(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    medias, errors = FETCH.all(Media, args)
    return Json(Media, errors)
  elif request.method == 'POST':
    #about to create a new Media instance
    media, errors = FACTORY.create(Media, args)
    return Json(media, errors)
  return Json(None)



@csrf_exempt
def media(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    media, errors = FETCH.all(Media, args)
    return Json(media, errors)
  elif request.method == 'POST':
    #updating the Media resource with this <id>
    media, errors = FACTORY.create(Media, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def media(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    media, errors = FETCH.all(Media, args)
    return Json(media, errors)
  elif request.method == 'POST':
    #updating the Media resource with this <id>
    media, errors = FACTORY.create(Media, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def menu(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    menus, errors = FETCH.all(Menu, args)
    return Json(Menu, errors)
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
    menu, errors = FETCH.all(Menu, args)
    return Json(menu, errors)
  elif request.method == 'POST':
    #updating the Menu resource with this <id>
    menu, errors = FACTORY.create(Menu, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def pages(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    pages, errors = FETCH.all(Page, args)
    return Json(Page, errors)
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
    page, errors = FETCH.all(Page, args)
    return Json(page, errors)
  elif request.method == 'POST':
    #updating the Page resource with this <id>
    page, errors = FACTORY.create(Page, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def page_sections(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    pagesections, errors = FETCH.all(PageSection, args)
    return Json(PageSection, errors)
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
    pagesection, errors = FETCH.all(PageSection, args)
    return Json(pagesection, errors)
  elif request.method == 'POST':
    #updating the PageSection resource with this <id>
    pagesection, errors = FACTORY.create(PageSection, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def permissions(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    permissions, errors = FETCH.all(Permission, args)
    return Json(Permission, errors)
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
    permission, errors = FETCH.all(Permission, args)
    return Json(permission, errors)
  elif request.method == 'POST':
    #updating the Permission resource with this <id>
    permission, errors = FACTORY.create(Permission, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def policies(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    policies, errors = FETCH.all(Policy, args)
    return Json(Policy, errors)
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
    policies, errors = FETCH.all(Policy, args)
    return Json(policies, errors)
  elif request.method == 'POST':
    #updating the Policy resource with this <id>
    policy, errors = FACTORY.create(Policy, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def roles(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    roles, errors = FETCH.all(Role, args)
    return Json(Role, errors)
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
    role, errors = FETCH.all(Role, args)
    return Json(role, errors)
  elif request.method == 'POST':
    #updating the Role resource with this <id>
    role, errors = FACTORY.create(Role, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def services(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    services, errors = FETCH.all(Service, args)
    return Json(Service, errors)
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
    service, errors = FETCH.all(Service, args)
    return Json(service, errors)
  elif request.method == 'POST':
    #updating the Service resource with this <id>
    service, errors = FACTORY.create(Service, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def sliders(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    sliders, errors = FETCH.all(Slider, args)
    return Json(Slider, errors)
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
    sliders, errors = FETCH.all(Slider, args)
    return Json(sliders, errors)
  elif request.method == 'POST':
    #updating the Slider resource with this <id>
    slider, errors = FACTORY.create(Slider, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def slider_images(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    sliderimages, errors = FETCH.all(SliderImage, args)
    return Json(SliderImage, errors)
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
    sliderimage, errors = FETCH.all(SliderImage, args)
    return Json(sliderimage, errors)
  elif request.method == 'POST':
    #updating the SliderImage resource with this <id>
    sliderimage, errors = FACTORY.create(SliderImage, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def statistics(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    statistics, errors = FETCH.all(Statistic, args)
    return Json(Statistic, errors)
  elif request.method == 'POST':
    #about to create a new Statistic instance
    statistic, errors = FACTORY.create(Statistic, args)
    return Json(statistic, errors)
  return Json(None)



@csrf_exempt
def statistic(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    statistic, errors = FETCH.all(Statistic, args)
    return Json(statistic, errors)
  elif request.method == 'POST':
    #updating the Statistic resource with this <id>
    statistic, errors = FACTORY.create(Statistic, args)
    return Json(action, errors)
  return Json(None)


@csrf_exempt
def subscribers(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    subscribers, errors = FETCH.all(Subscriber, args)
    return Json(Subscriber, errors)
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
    subscriber, errors = FACTORY.create(Subscriber, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def subscriber_email_preferences(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    subscriberemailpreferences, errors = FETCH.all(SubscriberEmailPreferences, args)
    return Json(SubscriberEmailPreferences, errors)
  elif request.method == 'POST':
    #about to create a new SubscriberEmailPreferences instance
    subscriberemailpreference, errors = FACTORY.create(SubscriberEmailPreferences, args)
    return Json(subscriberemailpreference, errors)
  return Json(None)



@csrf_exempt
def subscriber_email_preference(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    subscriberemailpreference, errors = FETCH.all(SubscriberEmailPreferences, args)
    return Json(subscriberemailpreference, errors)
  elif request.method == 'POST':
    #updating the SubscriberEmailPreference resource with this <id>
    subscriberemailpreference, errors = FACTORY.create(SubscriberEmailPreferences, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def tags(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    tags, errors = FETCH.all(Tag, args)
    return Json(Tag, errors)
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
    tag, errors = FETCH.all(Tag, args)
    return Json(tag, errors)
  elif request.method == 'POST':
    #updating the Tag resource with this <id>
    tag, errors = FACTORY.create(Tag, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def tag_collections(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    tagcollections, errors = FETCH.all(TagCollection, args)
    return Json(TagCollection, errors)
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
    tagcollection, errors = FETCH.all(TagCollection, args)
    return Json(tagcollection, errors)
  elif request.method == 'POST':
    #updating the TagCollection resource with this <id>
    tagcollection, errors = FACTORY.create(TagCollection, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def teams(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    teams, errors = FETCH.all(Team, args)
    return Json(Team, errors)
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
    team, errors = FETCH.all(Team, args)
    return Json(team, errors)
  elif request.method == 'POST':
    #updating the Team resource with this <id>
    team, errors = FACTORY.create(Team, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def testimonials(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    testimonials, errors = FETCH.all(Testimonial, args)
    return Json(Testimonial, errors)
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
    testimonial, errors = FETCH.all(Testimonial, args)
    return Json(testimonial, errors)
  elif request.method == 'POST':
    #updating the Testimonial resource with this <id>
    testimonial, errors = FACTORY.create(Testimonial, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def users(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    users, errors = FETCH.all(UserProfile, args)
    return Json(UserProfile, errors)
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
    user, errors = FETCH.all(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(UserProfile, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def user_households(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(UserProfile, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def user_household_actions(request, id, household_id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(UserProfile, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def user_actions(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(UserProfile, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def user_teams(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(UserProfile, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def user_testimonials(request, id):
  args = get_request_contents(request)
  args['id'] = id
  if request.method == 'GET':
    user, errors = FETCH.all(UserProfile, args)
    return Json(user, errors)
  elif request.method == 'POST':
    #updating the User resource with this <id>
    user, errors = FACTORY.create(UserProfile, args)
    return Json(action, errors)
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
    usergroup, errors = FETCH.all(UserGroup, args)
    return Json(usergroup, errors)
  elif request.method == 'POST':
    #updating the UserGroup resource with this <id>
    usergroup, errors = FACTORY.create(UserGroup, args)
    return Json(action, errors)
  return Json(None)



@csrf_exempt
def vendors(request):
  args = get_request_contents(request)
  if request.method == 'GET':
    vendors, errors = FETCH.all(Vendor, args)
    return Json(Vendor, errors)
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
    vendor, errors = FETCH.all(Vendor, args)
    return Json(vendor, errors)
  elif request.method == 'POST':
    #updating the Vendor resource with this <id>
    vendor, errors = FACTORY.create(Vendor, args)
    return Json(action, errors)
  return Json(None)
