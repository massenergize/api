import json
from _main_.utils.pagination import paginate
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from api.utils.filter_functions import get_messages_filter_params
from database.models import Message, Media, Team
from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
    InvalidResourceError,
    CustomMassenergizeError,
)
from _main_.utils.context import Context
from .utils import get_admin_communities, unique_media_filename
from _main_.utils.context import Context
from .utils import get_community, get_user
from sentry_sdk import capture_message
from typing import Tuple
from django.db.models import Q

class MessageStore:
    def __init__(self):
        self.name = "Message Store/DB"

    def get_message_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            message_id = args.pop("message_id", None) or args.pop("id", None)

            if not message_id:
                return None, InvalidResourceError()
            message = Message.objects.filter(pk=message_id).first()

            if not message:
                return None, InvalidResourceError()

            return message, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def reply_from_team_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            message_id = args.pop("message_id", None) or args.pop("id", None)

            if not message_id:
                return None, InvalidResourceError()
            message = Message.objects.filter(pk=message_id).first()

            if not message:
                return None, InvalidResourceError()

            return message, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def message_admin(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            community_id = args.pop("community_id", None)
            subdomain = args.pop("subdomain", None)
            user_name = args.pop("user_name", None)
            title = args.pop("title", None)
            email = args.pop("email", None) or context.user_email
            body = args.pop("body", None)
            file = args.pop("uploaded_file", None)
            parent = args.pop("parent", None)

            community, err = get_community(community_id, subdomain)
            if err:
                return None, err

            new_message = Message.objects.create(
                user_name=user_name,
                title=title,
                body=body,
                community=community,
                parent=parent,
            )
            new_message.save()
            user, err = get_user(context.user_id, email)
            if err:
                return None, err
            if user:
                new_message.user = user

            if file:

                file.name = unique_media_filename(file)

                media = Media.objects.create(
                    name=f"Messages: {new_message.title} - Uploaded File",
                    file=file,
                )
                media.save()
                new_message.uploaded_file = media

                new_message.save()
            # ----------------------------------------------------------------
            Spy.create_messaging_footage(
                messages=[new_message],
                context=context,
                type=FootageConstants.update(),
                notes="Reply from admin",
                related_users=[new_message.user],
            )
            # ----------------------------------------------------------------
            return new_message, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def message_team_admin(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            team_id = args.pop("team_id", None)
            title = args.pop("title", None)
            email = args.pop("email", None) or context.user_email
            body = args.pop("message", None) or args.pop("body", None)

            if not team_id:
                return None, InvalidResourceError()

            team = Team.objects.filter(pk=team_id).first()
            if not team:
                return None, InvalidResourceError()

            user, err = get_user(context.user_id)
            if err:
                return None, err
            user_name = args.pop("user_name", None) or user.full_name

            new_message = Message.objects.create(
                user_name=user_name,
                user=user,
                email=email,
                title=title,
                body=body,
                community=team.primary_community,
                team=team,
                is_team_admin_message=True,
            )
            new_message.save()
            return new_message, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def update_message_to_team_admin(
        self, context: Context, args
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            message_id = args.pop("message_id", None) or args.pop("id", None)
            title = args.pop("title", None)
            body = args.pop("message", None) or args.pop("body", None)

            if not message_id:
                return None, InvalidResourceError()
            message = Message.objects.filter(pk=message_id).first()

            if message.body != body or message.title != title:
                # message was modified in the admin portal
                admin_email = context.user_email
                body += (
                    "\n\n[This message was modified before forwarding by "
                    + admin_email
                    + "]"
                )
                message.title = title
                message.body = body
                message.save()
            # ----------------------------------------------------------------
            Spy.create_messaging_footage(
                messages=[message],
                context=context,
                teams=[message.team],
                related_users=[message.user],
                type=FootageConstants.forward(),
                notes="To Team Admins",
            )
            # ----------------------------------------------------------------
            return message, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def reply_from_community_admin(
        self, context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            message_id = args.pop("message_id", None) or args.pop("id", None)
            title = args.pop("title", None)
            body = args.pop("body", None)
            # attached_file = args.pop('attached_file', None)

            if not message_id:
                return None, InvalidResourceError()
            message = Message.objects.filter(pk=message_id).first()

            if not message:
                return None, InvalidResourceError()

            return message, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def delete_message(self, message_id, context) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            messages = Message.objects.filter(id=message_id)
            messages.update(is_deleted=True)
            message = messages.first()
            # TODO: also remove it from all places that it was ever set in many to many or foreign key

            # ----------------------------------------------------------------
            Spy.create_messaging_footage(
                messages=[message],
                context=context,
                type=FootageConstants.delete(),
                notes=f"Deleted ID({message_id})",
            )
            # ----------------------------------------------------------------
            return message, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_community_admin_messages(self, context: Context, args):
        message_ids = args.get("message_ids", [])

        try:
            filter_params = []

            if context.args.get("params", None):
                filter_params = get_messages_filter_params(context.args.get("params"))
            admin_communities, err = get_admin_communities(context)
            with_ids = Q()
            if message_ids:
                with_ids = Q(id__in=message_ids)

            if context.user_is_super_admin:
                messages = Message.objects.filter(
                    Q(
                        is_deleted=False,
                        is_team_admin_message=False,
                    ),
                    with_ids,
                    *filter_params
                ).distinct()
            elif context.user_is_community_admin:
                messages = Message.objects.filter(
                    Q(
                        is_deleted=False,
                        is_team_admin_message=False,
                        community__id__in=[c.id for c in admin_communities],
                    ),
                    with_ids,
                    *filter_params
                ).distinct()
            else:
                messages = []

            return messages, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

    def list_team_admin_messages(self, context: Context, args):
        message_ids = args.get("message_ids", [])
        with_ids = Q()
        if message_ids:
            with_ids = Q(id__in=message_ids)
        try:
            limit = context.args.get("limit")
            filter_params = []
            if context.args.get("params", None):
                filter_params = get_messages_filter_params(context.args.get("params"))
            if context.user_is_super_admin:
                messages = Message.objects.filter(
                    Q(is_deleted=False,
                      is_team_admin_message=True), with_ids, *filter_params
                ).distinct()
            elif context.user_is_community_admin:
                admin_communities, err = get_admin_communities(context)
                messages = Message.objects.filter(
                    Q(
                        is_deleted=False,
                        is_team_admin_message=True,
                        community__id__in=[c.id for c in admin_communities],
                    ),
                    with_ids,
                    *filter_params
                ).distinct()
            else:
                messages = []
            return messages, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
