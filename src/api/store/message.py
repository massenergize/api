from datetime import datetime, timedelta
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from api.tasks import send_scheduled_email
from api.utils.api_utils import is_admin_of_community, is_null
from api.utils.filter_functions import get_messages_filter_params
from database.models import Community, CommunityMember, Message, Media, Team, CommunityAdminGroup, UserProfile
from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
    InvalidResourceError,
    CustomMassenergizeError,
    NotAuthorizedError,
)
from _main_.utils.context import Context
from .utils import get_admin_communities, get_user_from_context, unique_media_filename
from _main_.utils.context import Context
from .utils import get_community, get_user
from sentry_sdk import capture_message
from typing import Tuple
from django.db.models import Q
from celery.result import AsyncResult
from django.utils import timezone


def get_schedule(schedule):
    if  not is_null(schedule):
       parsed_datetime = datetime.strptime(schedule, '%a, %d %b %Y %H:%M:%S %Z')
       formatted_date_string = timezone.make_aware(parsed_datetime)
       return formatted_date_string

    return  datetime.utcnow() + timedelta(minutes=1)
    


def get_message_recipients(audience, audience_type, sub_audience_type, communities):
    if not is_null(audience):
        if audience_type == "COMMUNITY_CONTACTS":
             if audience.lower() == "all":
                contacts = Community.objects.filter(is_deleted=False).only("owner_email", "id", "name")
             else:
                 audience = audience.split(",")
                 contacts = Community.objects.filter(id__in=audience).only("owner_email", "id", "name")
             return contacts
        
        if audience_type == "COMMUNITY_ADMIN" and sub_audience_type == "FROM_COMMUNITY":
            if communities and audience.lower() == "all":
                admins =  CommunityAdminGroup.objects.filter(id__in=communities.split(","), is_deleted=False).values_list("members", flat=True)
                return UserProfile.objects.filter(id__in=admins)
            
        if audience_type == "USERS" and sub_audience_type == "FROM_COMMUNITY":
            if communities and audience.lower() == "all":
                members =  CommunityMember.objects.filter(id__in=communities, is_deleted=False).values_list("members", flat=True)
                return UserProfile.objects.filter(id__in=members)
            
        if audience_type == "SUPER_ADMIN" and audience.lower() == "all":
            return UserProfile.objects.filter(is_super_admin=True)
            

        
        audience = audience.split(",")
        return UserProfile.objects.filter(id__in=audience)
    
    else:
        if audience_type == "COMMUNITY_ADMIN" and sub_audience_type == "ALL":
            admins =  CommunityAdminGroup.objects.filter(is_deleted=False).values_list("members", flat=True)
            return UserProfile.objects.filter(id__in=admins)
        elif audience_type == "USERS" and sub_audience_type == "ALL":
            return UserProfile.objects.filter(is_super_admin=False, is_community_admin=False)

    return None

class MessageStore:
    def __init__(self):
        self.name = "Message Store/DB"

    def get_message_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            message_id = args.pop("message_id", None) or args.pop("id", None)
            if not message_id:
                return None, InvalidResourceError()
            message = Message.objects.filter(pk=message_id).first()
            community_id = message.community.id if message.community else None

            if not is_admin_of_community(context,community_id):
                return None, NotAuthorizedError()

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
            sender_email = args.get("from") or context.user_email

            sender, error = get_user(user_id=None,email=sender_email)
            if error:
                return None, error

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
            user, err = get_user(context.user_id, sender_email)

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
                actor=sender,
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
            message_community_id = messages.first().community.id if messages.first().community else None
            if not is_admin_of_community(context, message_community_id):
                return None, NotAuthorizedError()
            
            schedule_info = messages.first().schedule_info or {}
            if schedule_info.get("schedule_id"):
                result = AsyncResult(schedule_info.get("schedule_id"))
                result.revoke()

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

            filter_params = get_messages_filter_params(context.get_params())

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
            filter_params = get_messages_filter_params(context.get_params())
            
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
        


    def send_message(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            audience_type = args.pop("audience_type", None)
            subject = args.get("subject", None)
            message = args.get("message", None)
            message_id = args.get("id", None)
            sub_audience_type = args.get("sub_audience_type", None)
            audience = args.get("audience", None)
            schedule = get_schedule(args.get("schedule", None))
            communities = args.get("community_ids", None)
            recipients = get_message_recipients(audience, audience_type, sub_audience_type, communities)
            

            if not recipients:
                return None, InvalidResourceError()
            
            user = get_user_from_context(context)
            if not user:
                return None, InvalidResourceError()
            

            email_list =  list(recipients.values_list("owner_email" if audience_type == "COMMUNITY_CONTACTS" else "email", flat=True))
        
            if message_id:
                messages = Message.objects.filter(pk=message_id)
                if not messages.first():
                    return None, InvalidResourceError()
                # revoke the previous task
                task_id = messages.first().schedule_info.get("schedule_id", None)
                if task_id:
                    result = AsyncResult(task_id)
                    result.revoke()
                # schedule new task and update message
                scheduled_at =messages.first().scheduled_at

                if messages.first().scheduled_at != schedule:
                   scheduled_at = schedule
                
                schedule_id = send_scheduled_email.apply_async(args=[ subject,message,email_list],eta=schedule).id
                schedule_info ={} if not args.get("schedule", None) else {"schedule_id": schedule_id,"recipients":{"audience_type":audience_type, "audience":audience, "sub_audience_type":sub_audience_type, "community_ids":communities}}
                messages.update(**{"schedule_info": schedule_info, "body": message, "title": subject, "scheduled_at":scheduled_at })
                return messages.first(), None
            else:
                schedule_id = send_scheduled_email.apply_async(args=[ subject,message,email_list],eta=schedule).id
                new_message = Message(
                title=subject,
                body=message,
                user=user,
                scheduled_at= schedule,
                schedule_info = {} if not args.get("schedule", None) else {"schedule_id": schedule_id, "recipients":{"audience_type":audience_type, "audience":audience, "sub_audience_type":sub_audience_type, "community_ids":communities}}
                )
                new_message.save()
                return new_message, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)
