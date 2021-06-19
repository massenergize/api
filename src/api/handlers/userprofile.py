"""Handler file for all routes pertaining to users"""
from functools import wraps
from _main_.utils.emailer.send_email import send_massenergize_email
from database.models import CommunityAdminGroup, UserProfile, Community
from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.userprofile import UserService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, community_admins_only, super_admins_only, login_required
from sentry_sdk import capture_message
# import pandas as pd
# for import contacts endpoint - accepts a csv file and verifies correctness of email address format
import csv, os, io, re


class UserHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = UserService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/users.info", self.info) 
    self.add("/users.create", self.create)
    self.add("/users.add", self.create)
    self.add("/users.list", self.list)
    self.add("/users.update", self.update)
    self.add("/users.delete", self.delete)
    self.add("/users.remove", self.delete)
    self.add("/users.actions.completed.add", self.add_action_completed)
    self.add("/users.actions.todo.add", self.add_action_todo)
    self.add("/users.actions.todo.list", self.list_actions_todo)
    self.add("/users.actions.completed.list", self.list_actions_completed)
    self.add("/users.actions.remove", self.remove_user_action)
    self.add("/users.households.add", self.add_household)
    self.add("/users.households.edit", self.edit_household)
    self.add("/users.households.remove", self.remove_household)
    self.add("/users.households.list", self.list_households)
    self.add("/users.events.list", self.list_events)

    #admin routes
    self.add("/users.listForCommunityAdmin", self.community_admin_list)
    self.add("/users.listForSuperAdmin", self.super_admin_list)
    self.add("/users.import", self.handle_contacts_csv)
    self.add("/users.test", self.test_route)


  @login_required
  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.get_user_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    args, err = (self.validator
      .expect("accepts_terms_and_conditions", bool, is_required=True)
      .expect("email", str, is_required=True)
      .expect("full_name", str, is_required=True)
      .expect("preferred_name", str, is_required=True)
      .expect("is_vendor", bool, is_required=True)
      .verify(context.args)
    )
    if err:
      return err
    user_info, err = self.service.create_user(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  @admins_only
  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    user_info, err = self.service.list_users(community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  @login_required
  def list_actions_todo(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.list_actions_todo(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def list_actions_completed(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.list_actions_completed(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def remove_user_action(self, request):
    context: Context = request.context
    args: dict = context.args
    user_action_id = args.get('user_action_id', None) or args.get("id", None)
    if not user_action_id:
      return MassenergizeResponse(error="invalid_resource")

    user_info, err = self.service.remove_user_action(context, user_action_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args,'id','user_id')
    user_id = args.pop('user_id', None)
    user_info, err = self.service.update_user(context, user_id, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    user_id = args.get("id", None) or args.get("user_id", None)
    user_info, err = self.service.delete_user(context, user_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    users, err = self.service.list_users_for_community_admin(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=users)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    users, err = self.service.list_users_for_super_admin(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=users)

  @login_required
  def add_action_todo(self, request):
    context: Context = request.context
    args, err = (self.validator
      .expect("action_id", str, is_required=True)
      .expect("household_id", str, is_required=False)
      .verify(context.args)
    )
    if err:
      return err
    user_info, err = self.service.add_action_todo(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def add_action_completed(self, request):
    context: Context = request.context
    
    args, err = (self.validator
      .expect("action_id", str, is_required=True)
      .expect("household_id", str, is_required=False)
      .verify(context.args)
    )
    if err:
      return err

    user_info, err = self.service.add_action_completed(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def list_households(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.get_user_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def remove_household(self, request):
    context: Context = request.context
    args: dict = context.args

    user_info, err = self.service.remove_household(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def add_household(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.add_household(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  @login_required
  def edit_household(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.edit_household(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  @login_required
  def list_events(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.list_events_for_user(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)
  

  @admins_only
  # @community_admins_only
  def handle_contacts_csv(self, request) -> (dict, MassEnergizeAPIError):
    context: Context = request.context
    args: dict = context.args
    # query users by user id, find the user that is sending the request
    user = UserProfile.objects.filter(id="837ef9ff-4065-4a41-b5d3-cfba7abc9108").first()
    # find the community that the user is the admin of. In the next section, populate user profiles with that information
    registered_community = None
    print(user.communities.all())
    for community in user.communities.all():
        admin_group = CommunityAdminGroup.objects.filter(community=community).first()
        if user in admin_group.members.all():
          break
    
    registered_community = community
    csv_ref = args['csv'].file    
    # csv_ref is a bytes object, we need a csv
    # so we copy it as a csv temporarily to the disk
    temporarylocation="testout.csv"
    with open(temporarylocation, 'wb') as out:
      # print("file converting")
      var = csv_ref.read()
      # print(var)
      out.write(var)
    with open(temporarylocation, "r") as f:
      reader = csv.DictReader(f, delimiter=",")
      for row in reader:
        column_list = list(row.keys())
        try:
          # prevents the first row (headers) from being read in as a user
          if row['First Name'] == column_list[0]:
            continue
          # verify correctness of email address
          regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
          try: 
            if(re.search(regex,row['Email'])):   
              # print("this row has a valid email")
              user = UserProfile.objects.filter(email=row['Email']).first()
              if not user:
                # print('user does not exist yet')
                new_user: UserProfile = UserProfile.objects.create(
                  full_name = row['First Name'] + ' ' + row['Last Name'], 
                  preferred_name = row['First Name'], 
                  email = row['Email'],
                  is_vendor = False, 
                  accepts_terms_and_conditions = False
                )   
                if registered_community:
                  new_user.communities.add(registered_community)
              else: 
                new_user: UserProfile = user  
              new_user.save()  
              # send email inviting user to complete their profile
              message = user.full_name + " invited you to join the following MassEnergize Community: " + registered_community
              send_massenergize_email(subject="Invitation to Join MassEnergize Community", msg=message, to=new_user.email)
            else:    
                return None, CustomMassenergizeError("Valid email required for sign up")
          except Exception as e:
            capture_message(str(e), level="error")
            print(str(e))
            return None, CustomMassenergizeError(e)
        except Exception as e:
          print(str(e))
          return None, CustomMassenergizeError(e)
    # and then delete it once we are done parsing it
    os.remove(temporarylocation)
    res = {'column names' : column_list}
    return MassenergizeResponse(data=res)

 
  def test_route(self, request):
    try:
      print('route is working up to here')
    except Exception as e:
      print(str(e))
    try: 
      registered_community = Community.objects.filter(name="Sustainable Students").first()
      user = UserProfile.objects.filter(email="arthorse17@gmail.com").first()
      if not user:
        new_user: UserProfile = UserProfile.objects.create(
          full_name = "Patrick Star", 
          preferred_name = "Patrick", 
          email = "arthorse17@gmail.com",
          is_vendor = False, 
          accepts_terms_and_conditions = False
        )   
        if registered_community:
          new_user.communities.add(registered_community)
      else: 
        new_user: UserProfile = user  
      new_user.save()  
      # send email inviting user to complete their profile
      print("type of user")
      print(type(user))
      message = user.full_name + " invited you to join the following MassEnergize Community: " + registered_community.name
      send_massenergize_email(subject="Invitation to Join MassEnergize Community", msg=message, to=new_user.email)
      print("email sent")
      dat = {"lovely":"lovely"}
      return MassenergizeResponse(data=dat)
    except Exception as e:
      capture_message(str(e), level="error")
      print(str(e))
      err = str(e)
      return MassenergizeResponse(error=err)