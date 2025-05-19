

import traceback
from typing import Tuple
from _main_.utils.constants import AudienceType, SubAudienceType
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.utils.api_utils import is_null
from api.utils.constants import BROADCAST_EMAIL_TEMPLATE
from database.models import Message, UserActionRel, UserProfile, Community, CommunityAdminGroup, CommunityMember
from _main_.utils.massenergize_logger import log

ALL = "all"

def get_message_recipients(audience, audience_type, community_ids,sub_audience_type) -> Tuple[list, str]:
    """
    This function is designed to return a list of recipients(emails) for a message based on the various parameters provided.
    
    Parameters:
    - audience (str): A string representing the audience to which the message will be delivered.
        It can have values like `COMMUNITY_CONTACTS`, `SUPER_ADMINS`, `COMMUNITY_ADMIN`, `USERS`, `ACTION_TAKERS`.
    - audience_type (str): A string that further categorizes the audience. It can alternate between
        `COMPLETED`, `TODO`, and `BOTH`.
    - community_ids (list): A list of community IDs that represent the communities targeted by the message.
    - sub_audience_type (str): This represents the type of users within the audience who will receive the message.
    
    Returns:
    A list of sets containing recipient email addresses. The sets are populated based on the `audience` and `audience_type`.

    """
    try:
        if is_null(audience): return None, None
        if community_ids and not isinstance(community_ids, list):
            community_ids = community_ids.split(",")

        if audience_type.lower() == AudienceType.COMMUNITY_CONTACTS.value.lower():
            communities = Community.objects.all()
            if audience.lower() != ALL.lower():
                audience = audience.split(",")
                communities = communities.filter(id__in=audience)
            return list(set(communities.values_list("owner_email", flat=True))), None
        
        elif audience_type.lower() == AudienceType.SUPER_ADMINS.value.lower():
            if audience.lower() == ALL.lower():
                return list(set(UserProfile.objects.filter(is_super_admin=True).values_list("email", flat=True))), None
            audience = audience.split(",")
        
        elif audience_type.lower() == AudienceType.COMMUNITY_ADMIN.value.lower():
            if audience.lower() == ALL.lower():
                if not community_ids:
                    return list(set(CommunityAdminGroup.objects.all().values_list("members__email", flat=True))), None
                return list(set(CommunityAdminGroup.objects.filter(community__id__in=community_ids).values_list("members__email", flat=True))), None
        
            audience = audience.split(",")
            
        elif audience_type.lower() == AudienceType.USERS.value.lower():
            if audience.lower() == ALL.lower():
                if not community_ids:
                    return list(set(UserProfile.objects.filter(is_super_admin=False, is_community_admin=False).values_list("email", flat=True))), None
                return list(set(CommunityMember.objects.filter(community__id__in=community_ids).values_list("user__email", flat=True))), None
            audience = audience.split(",")
            
        elif audience_type.lower() == AudienceType.ACTION_TAKERS.value.lower():
            audience = audience.split(",")
            user_action_rel = []
            if sub_audience_type.lower() == SubAudienceType.COMPLETED.value.lower():
                user_action_rel = UserActionRel.objects.filter(status=SubAudienceType.COMPLETED.value, action__id__in=audience).values_list("user__email", flat=True)
            elif sub_audience_type.lower() == SubAudienceType.TODO.value.lower():
                user_action_rel = UserActionRel.objects.filter(status=SubAudienceType.TODO.value, action__id__in=audience).values_list("user__email", flat=True)
                
            elif sub_audience_type.lower() == SubAudienceType.BOTH.value.lower():
                status = [SubAudienceType.COMPLETED.value, SubAudienceType.TODO.value]
                user_action_rel = UserActionRel.objects.filter(action__id__in=audience, status__in=status).values_list("user__email", flat=True)
                
            return list(set(user_action_rel)), None
            
        return list(set(UserProfile.objects.filter(id__in=audience).values_list("email", flat=True))), None
    except Exception as e:
        stacktrace = traceback.format_exc()
        log.exception(e)
        return None, stacktrace


        
def schedule_admin_messages(task):
    try:
    
        message = Message.objects.get(id=task.name)
        schedule_info = message.schedule_info or {}

        recipients = schedule_info.get("recipients", {})
        audience = recipients.get("audience", None)
        audience_type = recipients.get("audience_type", None)
        sub_audience_type = recipients.get("sub_audience_type", None)
        community_ids = recipients.get("community_ids", None)
        logo = recipients.get("logo", None)

        recipients, err = get_message_recipients(audience, audience_type, community_ids, sub_audience_type)
        if err:
            return None, err

        data = {"body": message.body, "subject": message.title, "image": logo}
        is_sent, err = send_massenergize_email_with_attachments(BROADCAST_EMAIL_TEMPLATE, data, recipients, None, None)
        if err:
            return None, err
        return is_sent, None
        
    except Exception as e:
      stacktrace = traceback.format_exc()
      return None, stacktrace
