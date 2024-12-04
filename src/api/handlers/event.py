"""Handler file for all routes pertaining to events"""

from _main_.utils.route_handler import RouteHandler
from api.services.event import EventService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from api.decorators import admins_only, cached_request, super_admins_only, login_required
from api.store.common import expect_media_fields


class EventHandler(RouteHandler):

    def __init__(self):
        super().__init__()
        self.service = EventService()
        self.registerRoutes()

    def registerRoutes(self) -> None:
        self.add("/events.info", self.info)
        self.add("/events.create", self.create)
        self.add("/events.add", self.submit)
        self.add("/events.submit", self.submit)
        self.add("/events.copy", self.copy)
        self.add("/events.list", self.list)
        self.add("/events.update", self.update)
        self.add("/events.delete", self.delete)
        self.add("/events.remove", self.delete)
        self.add("/events.rank", self.rank)
        self.add("/events.rsvp.list", self.get_rsvp_list)
        self.add("/events.rsvp.get", self.get_rsvp_status)
        self.add("/events.rsvp.update", self.rsvp_update)
        self.add("/events.rsvp.remove", self.rsvp_remove)
        self.add("/events.todo", self.save_for_later)
        self.add("/events.exceptions.list", self.list_exceptions)
        self.add("/events.date.update", self.update_recurring_date)
        self.add("/events.share", self.share_event)
        self.add("/events.reminders.settings.create", self .create_event_reminder_settings)
        self.add("/events.reminders.settings.delete", self.delete_event_reminder_settings)

        # admin routes
        self.add("/events.listForCommunityAdmin", self.community_admin_list)
        self.add("/events.others.listForCommunityAdmin", self.fetch_other_events_for_cadmin)
        self.add("/events.listForSuperAdmin", self.super_admin_list)

    def info(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("event_id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        event_info, err = self.service.get_event_info(context, args)
        if err:
            return err

        return MassenergizeResponse(data=event_info)

    @admins_only
    def copy(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("event_id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        event_info, err = self.service.copy_event(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @admins_only
    def get_rsvp_list(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("event_id", int)
        # TODO: return list for all events from a community
        # self.validator.expect("community_id", int)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        event_info, err = self.service.get_rsvp_list(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @login_required
    def get_rsvp_status(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("event_id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        event_info, err = self.service.get_rsvp_status(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @login_required
    def rsvp_update(self, request) -> function:
        context: Context = request.context
        args:dict = context.args

        self.validator.expect("event_id", int, is_required=True)
        self.validator.expect("status", str, is_required=False)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        event_info, err = self.service.rsvp_update(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @login_required
    def rsvp_remove(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("rsvp_id", int)
        self.validator.expect("event_id", int)
        args, err = self.validator.verify(args)

        if err:
            return err

        event_info, err = self.service.rsvp_remove(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @login_required
    def save_for_later(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("event_id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        event_info, err = self.service.get_event_info(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @admins_only
    def create(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect('name', str, is_required=True, options={"min_length": 5, "max_length": 100})
        self.validator.expect('tags', list)
        self.validator.expect('is_global', bool)
        self.validator.expect('archive', bool)
        self.validator.expect('is_published', bool)
        self.validator.expect('is_recurring', bool)
        self.validator.expect('is_approved', bool)
        self.validator.expect('have_address', bool)
        self.validator.expect('location', 'location')
        self.validator.expect('rsvp_enabled', bool)
        self.validator.expect('rsvp_email', bool)
        self.validator.expect("image", "str_list")
        self.validator.expect("publicity", str)
        self.validator.expect("event_type", str)
        self.validator.expect("publicity_selections", list)
        self.validator.expect("add_to_home_page", bool, is_required=False)
        args, err = self.validator.verify(args)

        if err:
            return err

        # not user submitted
        args["is_approved"] = args.pop("is_approved", True)

        event_info, err = self.service.create_event(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @login_required
    def submit(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect('name', str, is_required=True, options={"min_length": 5, "max_length": 100})
        self.validator.expect('tags', list)
        self.validator.expect('is_recurring', bool)
        self.validator.expect('have_address', bool)
        self.validator.expect('location', 'location')
        self.validator.expect('rsvp_enabled', bool)
        self.validator.expect('rsvp_email', bool)
        self.validator.expect('event_id', str)
        expect_media_fields(self)

        args, err = self.validator.verify(args)

        if err:
            return err

        # user submitted event, so notify the community admins
        user_submitted = True

        is_edit = args.get("event_id", None)

        if is_edit:
            event_info, err = self.service.update_event(context, args, user_submitted)
        else:
            args["is_approved"] = False
            event_info, err = self.service.create_event(context, args, user_submitted)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    # lists any recurring event exceptions for the event
    def list_exceptions(self, request):
        context: Context = request.context
        args: dict = context.args

        exceptions, err = self.service.list_recurring_event_exceptions(context, args)

        if err:
            return err

        return MassenergizeResponse(data=exceptions)
    
    @cached_request
    def list(self, request):

        context: Context = request.context
        args: dict = context.args

        self.validator.expect("community_id", is_required=False)
        self.validator.expect("subdomain", is_required=False)
        self.validator.expect("user_id", is_required=False)
        self.validator.expect("community_ids", list, is_required=False)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        event_info, err = self.service.list_events(context, args)

        if err:
            return err
        return MassenergizeResponse(data=event_info)

    def update_recurring_date(self, request):
        context: Context = request.context
        args: dict = context.args
        event_info, err = self.service.update_recurring_event_date(context, args)

        if err:
            return err
        return MassenergizeResponse(data=event_info)

    # @admins_only
    # changed to @Login_Required so I can edit the event as the creator and admin
    @login_required
    def update(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.rename('community', 'community_id')
        self.validator.expect('community_id', int, is_required=False)
        self.validator.expect('event_id', int, is_required=True)
        self.validator.expect('name', str, is_required=False, options={"min_length": 5, "max_length": 100})
        self.validator.expect('tags', list)
        self.validator.expect('is_global', bool)
        self.validator.expect('archive', bool)
        self.validator.expect('is_published', bool)
        self.validator.expect('is_approved', bool)
        self.validator.expect('have_address', bool)
        self.validator.expect('location', 'location')
        self.validator.expect('is_recurring', bool)
        self.validator.expect('upcoming_is_cancelled', bool)
        self.validator.expect('upcoming_is_rescheduled', bool)
        self.validator.expect('rsvp_enabled', bool)
        self.validator.expect('rsvp_email', bool)
        self.validator.expect("image", "str_list")
        self.validator.expect("publicity", str)
        self.validator.expect("event_type", str)
        self.validator.expect("publicity_selections", "str_list")
        self.validator.expect("shared_to", "str_list")
        self.validator.expect("settings", dict, is_required=False)

        expect_media_fields(self)
        args, err = self.validator.verify(args)

        if err:
            return err

        event_info, err = self.service.update_event(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @admins_only
    def rank(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect('id', int, is_required=True)
        self.validator.expect('rank', int, is_required=True)
        self.validator.rename('event_id', 'id')

        args, err = self.validator.verify(args)
        if err:
            return err

        event_info, err = self.service.rank_event(args, context)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @admins_only
    def delete(self, request):
        context: Context = request.context
        args: dict = context.args
        event_id = args.get("event_id", None)
        event_info, err = self.service.delete_event(context, event_id)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @admins_only
    def community_admin_list(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("community_id", int, is_required=False)
        args, err = self.validator.verify(args)
        if err:
            return err

        events, err = self.service.list_events_for_community_admin(context, args)
        if err:
            return err

        return MassenergizeResponse(data=events)

    @admins_only
    def fetch_other_events_for_cadmin(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("community_ids", "str_list", is_required=True)
        self.validator.expect("exclude", bool, is_required=False)

        args, err = self.validator.verify(args)
        if err:
            return err

        events, err = self.service.fetch_other_events_for_cadmin(context, args)
        if err:
            return err
        return MassenergizeResponse(data=events)

    @super_admins_only
    def super_admin_list(self, request):
        context: Context = request.context
        events, err = self.service.list_events_for_super_admin(context)
        if err:
            return err

        return MassenergizeResponse(data=events)

    @admins_only
    def share_event(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("event_id", int, is_required=True)
        self.validator.expect("shared_to", "str_list", is_required=True)
        args, err = self.validator.verify(args, strict=True)

        if err:
            return err

        event_info, err = self.service.share_event(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @admins_only
    def create_event_reminder_settings(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("event_id", int, is_required=True)
        self.validator.expect("community_ids", "str_list", is_required=True)
        self.validator.expect("when_first_posted", bool, is_required=False)
        self.validator.expect("within_30_days", bool, is_required=False)
        self.validator.expect("within_1_week", bool, is_required=False)
        self.validator.expect("never", bool, is_required=False)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        event_info, err = self.service.create_event_reminder_settings(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)

    @admins_only
    def delete_event_reminder_settings(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("nudge_settings_id", str, is_required=True)

        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        event_info, err = self.service.delete_event_reminder_settings(context, args)
        if err:
            return err
        return MassenergizeResponse(data=event_info)