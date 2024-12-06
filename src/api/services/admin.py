from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize
from _main_.utils.pagination import paginate
from api.store.admin import AdminStore
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT, ME_LOGO_PNG
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments, send_massenergize_rich_email
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL, IS_PROD, IS_CANARY
from api.utils.constants import CONTACT_ADMIN_EMAIL_TEMPLATE, NEW_ADMIN_EMAIL_TEMPLATE
from api.utils.filter_functions import sort_items
from .utils import send_slack_message
from _main_.utils.massenergize_logger import log
from typing import Tuple

class AdminService:
    """
    Service Layer for all the admins
    """

    def __init__(self):
        self.store = AdminStore()

    def add_super_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
      try:
        admin, err = self.store.add_super_admin(context, args)
        if err:
            return None, err

        subject = 'Welcome to the MassEnergize Team'
        content_variables = {
            'name': admin.full_name,
            'adminlink': ADMIN_URL_ROOT,
            'admintype': 'Super',
            'admintext': "Now that you are a super admin, you have access the MassEnergize admin website at %s. You have full control over the content of our sites, can publish new communities and add new admins" % (ADMIN_URL_ROOT),
            "me_logo": ME_LOGO_PNG,
            "subject": "Welcome to the MassEnergize Team"
        }

        send_massenergize_email_with_attachments(NEW_ADMIN_EMAIL_TEMPLATE, content_variables, [admin.email], None, None, None)

        # sent from MassEnergize to cadmins
        # send_massenergize_rich_email(
        #     subject, admin.email, 'new_admin_email.html', content_variables, None)
        return serialize(admin, full=True), None
      except Exception as e:
        log.exception(e)
        return None, CustomMassenergizeError(e)

    def remove_super_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        admin, err = self.store.remove_super_admin(context, args)
        if err:
            return None, err
        return serialize(admin, full=True), None

    def list_super_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        admins, err = self.store.list_super_admin(context, args)
        if err:
            return None, err
        sorted = sort_items(admins, context.get_params())
        return paginate(sorted, context.get_pagination_data()), None

    def add_community_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
      try:    
        res, err = self.store.add_community_admin(context, args)
        if err:
            return None, err

        subject = 'Welcome to the MassEnergize Team'
        content_variables = {
            'name': res["name"],
            'admin_link': ADMIN_URL_ROOT,
            "community_name": res["community_name"],
            'sandbox_link': f"{COMMUNITY_URL_ROOT}/{res['subdomain']}?sandbox=true",
            'portal_link':  f"{COMMUNITY_URL_ROOT}/{res['subdomain']}",
            'admin_type': 'Community',
            "me_logo": ME_LOGO_PNG,
            "subject": "Welcome to the MassEnergize Team"
        }
        #sent from MassEnergize support
        # send_massenergize_rich_email(subject, res["email"], 'new_admin_email.html', content_variables, None)
        send_massenergize_email_with_attachments(NEW_ADMIN_EMAIL_TEMPLATE, content_variables, [res["email"]], None, None, None)
        res["user"] = serialize(res.get("user"))
        return res, None
      except Exception as e:
        log.exception(e)
        return None, CustomMassenergizeError(e)

    def remove_community_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        admin, err = self.store.remove_community_admin(context, args)
        if err:
            return None, err
        return serialize(admin, full=True), None

    def list_community_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        admins, err = self.store.list_community_admin(context, args)
        if err:
            return None, err
        return  serialize(admins), None

    def message_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
      try:
        message, err = self.store.message_admin(context, args)
        if err:
            return None, err

        # Original comment: dont want to send emails all the time, just show up in the admin site and if they want they can send emails
        # Now community admins are requesting e-mail messages.  We don't have contact preferences defined yet but will do that.
        # For now, send e-mail to primary community contact for a site
        admin_email = message.community.owner_email
        admin_name = message.community.owner_name
        first_name = admin_name.split(" ")[0]
        if not first_name or first_name == "":
            first_name = admin_name

        # subject = 'A message was sent to the Community Admin for ' + message.community.name

        content_variables = {
            'name': first_name,
            'message_url': f"{ADMIN_URL_ROOT}/admin/edit/{message.id}/message",
            "community_name": message.community.name,
            "from_name": message.user_name,
            "email": message.email,
            "subject": message.title,
            "message_body": message.body,
            "me_logo": ME_LOGO_PNG
        }
        # sent from MassEnergize to cadmins
        # send_massenergize_rich_email(subject, admin_email, 'contact_admin_email.html', content_variables, None)
        send_massenergize_email_with_attachments(CONTACT_ADMIN_EMAIL_TEMPLATE, content_variables, [admin_email], None, None, None)


        if IS_PROD or IS_CANARY:
          send_slack_message(
            #SLACK_COMMUNITY_ADMINS_WEBHOOK_URL, {
            SLACK_SUPER_ADMINS_WEBHOOK_URL, {
            "content": "Message to Community Admin for "+message.community.name,
            "from_name": message.user_name,
            "email": message.email,
            "subject": message.title,
            "message": message.body,
            "url": f"{ADMIN_URL_ROOT}/admin/edit/{message.id}/message",
            "community": message.community.name
        }) 

        return serialize(message), None
      except Exception as e:
        log.exception(e)
        return None, CustomMassenergizeError(e)
   
    def list_admin_messages(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        admins_messages, err = self.store.list_admin_messages(context, args)
        if err:
            return None, err
        sorted = sort_items(admins_messages, context.get_params())
        return paginate(sorted, context.get_pagination_data()), None
