"""Handler file for all routes pertaining to users"""
from functools import wraps
from _main_.utils.emailer.send_email import send_massenergize_email
from database.models import CommunityAdminGroup, UserProfile, Community, Team
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
from django.utils import timezone
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
    self.add("/users.checkImported", self.check_user_imported)
    self.add("/users.completeImported", self.complete_imported_user)

    #admin routes
    self.add("/users.listForCommunityAdmin", self.community_admin_list)
    self.add("/users.listForSuperAdmin", self.super_admin_list)
    self.add("/users.import", self.handle_contacts_csv)
    self.add("/users.adminCommunity", self.get_admin_community)
    

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
      .expect("community_id", int)
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

  # lists users that are in the community for cadmin
  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    users, err = self.service.list_users_for_community_admin(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=users)
  
  
  @admins_only
  def community_team_list(self, request):
    try:
      context: Context = request.context
      print(context)
      args: dict = context.args
      community_id = args.pop("community_id", None)
      print(community_id)
      comm = Community.objects.filter(id=community_id).first()
      print(comm)
      teams = Team.objects.filter(community=comm).all().values_list('name', flat=True)
      teams=list(teams)
      print(teams)
    except Exception as e:
      print(str(e))
      return MassenergizeResponse(error=str(e), status=False)
    
    return MassenergizeResponse(data=teams)
    

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
  
  # lists id of community for which the user sending the request is the admin
  @admins_only
  def get_admin_community(self, request):
    context: Context = request.context
    args: dict = context.args
    # query users by user id, find the user that is sending the request
    cadmin = UserProfile.objects.filter(id=context.user_id).first()
    # find the community that the user is the admin of. In the next section, populate user profiles with that information
    try:
      print(cadmin.communities.all())
      for community in cadmin.communities.all():
          admin_group = CommunityAdminGroup.objects.filter(community=community).first()
          if cadmin in admin_group.members.all():
            return MassenergizeResponse(data={"id":community.id, "subdomain":str(community.subdomain)})
    except Exception as e:
      print(str(e))
    return CustomMassenergizeError("You are not the administrator of any community")
    
  # checks whether a user profile has been temporarily set up as a CSV
  def check_user_imported(self, request):
    context: Context = request.context
    args: dict = context.args
    email_address = args.get('email', None)
    print(email_address)
    profile = UserProfile.objects.filter(email=email_address).first()
    if profile.accepts_terms_and_conditions:
      name = profile.full_name.split()
      first_name = name[0]
      last_name = name[1]
      return MassenergizeResponse(data={"imported":True, "firstName": first_name, "lastName": last_name, "preferredName": first_name})
    return MassenergizeResponse(data={"imported":False})

  @login_required
  def complete_imported_user(self, request):
    try:
      context: Context = request.context
      args: dict = context.args
      email_address = args['email']
      imported = None
      profile = UserProfile.objects.filter(email=email_address).first()
      if profile.accepts_terms_and_conditions:
        return MassenergizeResponse(data={"completed":False}), None
    except Exception as e:
      return None, MassEnergizeAPIError(error=str(e))
    return MassenergizeResponse(data={"completed":True}), None

  @admins_only
  # @community_admins_only (not set this way for testing purposes)
  def handle_contacts_csv(self, request):
    context: Context = request.context
    args: dict = context.args
    # query users by user id, find the user that is sending the request
    cadmin = UserProfile.objects.filter(id=context.user_id).first()
    # find the community that the user is the admin of. In the next section, populate user profiles with that information
    registered_community = None
    for community in cadmin.communities.all():
        admin_group = CommunityAdminGroup.objects.filter(community=community).first()
        if cadmin in admin_group.members.all():
          break
    registered_community = community
    
    # find the community within the team that the 
    csv_ref = args['csv'].file 
    first_name_field = args['first_name_field']
    last_name_field = args['last_name_field']   
    email_field = args['email_field']
    # csv_ref is a bytes object, we need a csv
    # so we copy it as a csv temporarily to the disk
    temporarylocation="testout.csv"
    with open(temporarylocation, 'wb') as out:
      var = csv_ref.read()
      out.write(var)
    with open(temporarylocation, "r") as f:
      reader = csv.DictReader(f, delimiter=",")
      for row in reader:
        column_list = list(row.keys())
        try:
          # prevents the first row (headers) from being read in as a user
          if row[first_name_field] == column_list[0]:
            continue
          # verify correctness of email address
          regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
          try: 
            if(re.search(regex,row[email_field])):   
              user = UserProfile.objects.filter(email=row[email_field]).first()
              if not user:
                if row[email_field] == "" or not row[email_field]:
                  return None, CustomMassenergizeError("One of more of your user(s) lacks a valid email address. Please make sure all your users have valid email addresses listed.")
                new_user: UserProfile = UserProfile.objects.create(
                  full_name = row[first_name_field] + ' ' + row[last_name_field], 
                  preferred_name = row[first_name_field], 
                  email = row[email_field],
                  is_vendor = False, 
                  accepts_terms_and_conditions = False
                )
                new_user.save() 
                if registered_community:
                  new_user.communities.add(registered_community)
              else: 
                new_user: UserProfile = user  
              if args['team_name'] != "none":
                team = Team.objects.filter(name=args['team_name']).first()
                team.members.add(new_user)
                team.save()
              new_user.save()
              # send email inviting user to complete their profile
              message = ""
              message += cadmin.full_name + " invited you to join the following MassEnergize Community: " + registered_community.name + "\n"
              if args["message"] != "":
                message += "They have included a message for you here:\n"
                message += args["message"]
              '''if team:
                message += "You have been assigned to the following team: " + team.name + "\n"'''
              link = "localhost:3000/" + str(registered_community.subdomain) + "/signup"
              print(link)
              message += "Use the following link to join " + registered_community.name + ": " + link
              send_massenergize_email(subject= cadmin.full_name + " invited you to join a MassEnergize Community", msg=message, to=new_user.email)
            else:    
                return MassenergizeResponse(data=None, error="One of more of your user(s) lacks a valid email address. Please make sure all your users have valid email addresses listed.")
                # return None, CustomMassenergizeError("One of more of your user(s) lacks a valid email address. Please make sure all your users have valid email addresses listed.")
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

 
  