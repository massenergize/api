"""Handler file for all routes pertaining to users"""
from _main_.utils.route_handler import RouteHandler
from api.services.userprofile import UserService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import NotAuthorizedError
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only, login_required


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
        self.add("/users.listForPublicView", self.list_publicview)  # NOT USED
        self.add("/users.validate.username", self.validate_username)

        # admin routes
        self.add("/users.listForCommunityAdmin", self.community_admin_list)
        self.add("/users.listForSuperAdmin", self.super_admin_list)
        self.add("/users.import", self.import_users)
        self.add("/users.mou.accept", self.accept_mou)
        self.add("/users.update.loosedUser", self.update_loosed_user)
        self.add("/users.get.loosedUser", self.get_loosed_user)

        self.add("/users.get.visits", self.fetch_user_visits)

    @admins_only
    def fetch_user_visits(self, request):
        context: Context = request.context
        args: dict = context.args
        args, err = self.validator.expect("id", str, is_required=True).verify(
            context.args
        )
        if err:
            return err
        visits, err = self.service.fetch_user_visits(context, args)
        if err:
            return err
        return MassenergizeResponse(data=visits)

    @admins_only
    def accept_mou(self, request):
        context: Context = request.context
        args: dict = context.args
        args, err = (
            self.validator.expect("accept", bool, is_required=True)
            # .expect("email", str) # For postman tests
            .expect("policy_key", str, is_required=True).verify(context.args)
        )
        if err:
            return err
        response, err = self.service.accept_mou(args, context)
        if err:
            return err
        return MassenergizeResponse(data=response)

    @login_required
    def info(self, request):
        context: Context = request.context
        args: dict = context.args
        user_info, err = self.service.get_user_info(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    def validate_username(self, request):
        context: Context = request.context
        args: dict = context.args

        data, err = self.service.validate_username(args.get("username"))
        if err:
            return MassenergizeResponse(error=err)
        return MassenergizeResponse(data=data)

    def create(self, request):
        context: Context = request.context
        args: dict = context.args
        args, err = (
            self.validator.expect(
                "accepts_terms_and_conditions", bool, is_required=True
            )
            .expect("email", str, is_required=True)
            .expect("full_name", str, is_required=True)
            .expect("preferred_name", str, is_required=True)
            .expect("is_vendor", bool)
            .expect("is_guest", bool)
            .expect("community_id", int)
            .verify(context.args)
        )
        if err:
            return err
        user_info, err = self.service.create_user(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @admins_only
    def list(self, request):
        context: Context = request.context
        args: dict = context.args
        community_id = args.pop("community_id", None)
        user_info, err = self.service.list_users(context, community_id)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    def list_publicview(self, request):
        context: Context = request.context
        args: dict = context.args
        args, err = (
            self.validator.expect("community_id", int, is_required=True)
            .expect("min_points", int, is_required=False)
            .verify(context.args)
        )
        if err:
            return err

        user_info, err = self.service.list_publicview(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def list_actions_todo(self, request):
        context: Context = request.context
        args: dict = context.args
        user_todo_actions, err = self.service.list_actions_todo(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_todo_actions)

    @login_required
    def list_actions_completed(self, request):
        context: Context = request.context
        args: dict = context.args
        user_completed_actions, err = self.service.list_actions_completed(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_completed_actions)

    @login_required
    def remove_user_action(self, request):
        context: Context = request.context
        args: dict = context.args
        user_action_id = args.get("user_action_id", None) or args.get("id", None)
        if not user_action_id:
            return MassenergizeResponse(error="invalid_resource")

        user_info, err = self.service.remove_user_action(context, user_action_id)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def update(self, request):
        context: Context = request.context
        args: dict = context.args

        args, err = (
            self.validator.rename("user_id", "id")
            .expect("id", str, is_required=False)
            .verify(context.args)
        )
        if err:
            return err

        # user info is now taken from context
        # strip user_id, id out of args if not using
        # validate that id passed in is
        id = args.pop("id", None)
        if id and id != context.user_id:
            return None, NotAuthorizedError()

        user_info, err = self.service.update_user(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def delete(self, request):
        context: Context = request.context
        args: dict = context.args
        user_id = args.get("id", None) or args.get("user_id", None)
        user_info, err = self.service.delete_user(context, user_id)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    # lists users that are in the community for cadmin
    @admins_only
    def community_admin_list(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("user_emails", "str_list", is_required=False)
        self.validator.expect("user_ids", "str_list", is_required=False)
        
        args, err = self.validator.verify(args)
        if err:
            return err
        users, err = self.service.list_users_for_community_admin(context, args)
        if err:
            return err

        return MassenergizeResponse(data=users)

    @super_admins_only
    def super_admin_list(self, request):
        context: Context = request.context
        args: dict = context.args
        args, err = (
            self.validator.expect("user_emails", "str_list", is_required=False)
            .expect("community_ids", "str_list", is_required=False)
            .expect("user_ids", "str_list", is_required=False)
            .verify(args)
        )
        if err:
            return err
        users, err = self.service.list_users_for_super_admin(context, args)
        if err:
            return err

        return MassenergizeResponse(data=users)


    @login_required
    def add_action_todo(self, request):
        context: Context = request.context
        args, err = (
            self.validator.expect("action_id", str, is_required=True)
            .expect("household_id", str, is_required=False)
            .expect("date_completed", "date", is_required=False)
            .verify(context.args)
        )
        if err:
            return err

        user_info, err = self.service.add_action_todo(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def add_action_completed(self, request):
        context: Context = request.context

        args, err = (
            self.validator.expect("action_id", int, is_required=True)
            .expect("household_id", int, is_required=False)
            .expect("date_completed", "date", is_required=False)
            .verify(context.args)
        )
        if err:
            return err

        user_info, err = self.service.add_action_completed(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def list_households(self, request):
        context: Context = request.context
        args: dict = context.args
        user_info, err = self.service.get_user_info(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def remove_household(self, request):
        context: Context = request.context
        args: dict = context.args

        user_info, err = self.service.remove_household(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def add_household(self, request):
        context: Context = request.context
        args: dict = context.args
        user_info, err = self.service.add_household(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def edit_household(self, request):
        context: Context = request.context
        args: dict = context.args
        user_info, err = self.service.edit_household(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    @login_required
    def list_events(self, request):
        context: Context = request.context
        args: dict = context.args
        user_info, err = self.service.list_events_for_user(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)

    # checks whether a user profile has been temporarily set up as a CSV
    def check_user_imported(self, request):
        context: Context = request.context
        args: dict = context.args

        args, err = self.validator.expect("email", str, is_required=True).verify(
            context.args
        )
        if err:
            return err

        imported_info, err = self.service.check_user_imported(context, args)
        if err:
            return err
        return MassenergizeResponse(data=imported_info)

    # @login_required
    # def complete_imported_user(self, request):
    #  context: Context = request.context
    #  args: dict = context.args
    #  imported_info, err = self.service.complete_imported_user(context, args)
    #  if err:
    #    return err
    #  return MassenergizeResponse(data=imported_info)

    @admins_only
    # Community or Super Admins can do this
    def import_users(self, request):
        context: Context = request.context
        args: dict = context.args

        if args.get("csv", None):
            return self.import_from_csv(context, args)
        else:
            return self.import_from_list(context, args)

    # Community or Super Admins can do this
    def import_from_csv(self, context, args):
        args, err = (
            self.validator.expect("community_id", int, is_required=True)
            .expect("csv", "file", is_required=True)
            .expect("first_name_field", str, is_required=True)
            .expect("last_name_field", str, is_required=True)
            .expect("email_field", str, is_required=True)
            .expect("team_id", int, is_required=False)
            .verify(context.args)
        )
        if err:
            return err
        info, err = self.service.import_from_csv(context, args)
        if err:
            return err
        return MassenergizeResponse(data=info)

    # Community or Super Admins can do this
    def import_from_list(self, context, args):
        args, err = (
            self.validator.expect("community_id", int, is_required=True)
            .expect("names", "str_list")
            .expect("first_names", "str_list")
            .expect("last_names", "str_list")
            .expect("emails", "str_list", is_required=True)
            .expect("team_id", int, is_required=False)
            .verify(context.args)
        )
        if err:
            return err
        info, err = self.service.import_from_list(context, args)
        if err:
            return err
        return MassenergizeResponse(data=info)
    

    def update_loosed_user(self, request):
        context:Context = request.context
        args:dict = context.args

        args, err = (
            self.validator.expect("id", str, is_required=True)
            .expect("email", str, is_required=False)
            .expect("full_name", str, is_required=False)
            .expect("preferred_name", str, is_required=False)
            .expect("follow_id", str, is_required=True)
            .verify(args, strict=True)
        )
        if err:
            return err
        user_info, err = self.service.update_loosed_user(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)
    

    def get_loosed_user(self, request):
        context:Context = request.context
        args:dict = context.args

        args, err = (
            self.validator.expect("id", str, is_required=False)
            .expect("email", str, is_required=False)
            .verify(args, strict=True)
        )
        if err:
            return err
        user_info, err = self.service.get_loosed_user(context, args)
        if err:
            return err
        return MassenergizeResponse(data=user_info)
