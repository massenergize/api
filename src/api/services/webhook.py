import logging

from sentry_sdk import capture_message
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.context import Context
from typing import Tuple
from api.services.message import MessageService
from api.tasks import deactivate_user
from api.constants import GUEST_USER

from database.models import UserProfile
import re
import urllib.parse

from _main_.utils.massenergize_errors import CustomMassenergizeError

ONE_DAY = 60*60*24
HARD_BOUNCE="HardBounce"
WELCOME_MESSAGE="Welcome Message From MassEnergize"



def extract_email_content(text):
  subject_match = re.search(r"Subject: (.+)\n", text)
  if subject_match:
      subject = subject_match.group(1)
  else:
      subject = None

  email_match = re.search(r"From: (.+)\n", text)
  if email_match:
      email = email_match.group(1)
      email = re.search(r"\(([^)]+)\)", email).group(1)
  else:
      email = None

  return subject, email

def get_messsage_id_from_link_list(url_parts):
    try:
        edit_index = url_parts.index('edit')
        message_id = url_parts[edit_index + 1]
        
        if message_id.isdigit():
            return message_id
        
        return None
    except ValueError:
        logging.error("INBOUND_PROCESSING:ValueError while extracting message id from the url")
        return None


def extract_msg_id(text):
    try:
        url_pattern = r"<(https?:\\/\\/click\.pstmrk\.it[^\s>]+)>"
        match = re.search(url_pattern, text)
        
        if not match:
            logging.error("INBOUND_PROCESSING:Could not extract message id from the email body")
            return None
        
        url = match.group(1)
        
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        path = urllib.parse.unquote(path)
        splitted_path_list = path.split("/")
        
        message_id = get_messsage_id_from_link_list(splitted_path_list)
        
        if not message_id:
            logging.error("INBOUND_PROCESSING:Incorrect message id format in the email body")
            return None
        
        return message_id
    
    except Exception as e:
        logging.error(f"INBOUND_PROCESSING:Exception while extracting message id from the email body: {str(e)}")
        return None
      

class WebhookService:
  """
  Service Layer for all the webhooks
  """

  def __init__(self):
    self.message_service = MessageService()

    pass

  def bounce_email_webhook(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    email = args.get("Email")
    bounce_type = args.get("Type")
    email_subject = args.get("Subject")

    if bounce_type == HARD_BOUNCE and email_subject == WELCOME_MESSAGE:
        user = UserProfile.objects.filter(email=email).first()
        if user:
            user_info = (user.user_info or {}).get("user_type")
            if user_info == GUEST_USER:
                deactivate_user.apply_async((user.email,),countdown=ONE_DAY)

    return {"success":True}, None
  
  def process_inbound_webhook(self, context: Context, args):
    try:
        reply = args.get("StrippedTextReply")
        text_body = args.get("TextBody")
        from_email = args.get("From")
        
        if not text_body:
            logging.error("INBOUND_PROCESSING:No text body found in the inbound email")
            return None,  CustomMassenergizeError("No text body found in the inbound email")

        split_body = text_body.strip().split("Here is a copy of the message:")
        
        if len(split_body) < 2:   # will probably be a postmark test
            return {"success": False}, None
        
        user_msg_content = split_body[1].strip().split("If possible, please reply through the admin portal rather than")[0].strip()
        subject, email = extract_email_content(user_msg_content)

        db_msg_id = extract_msg_id(text_body)

        if not db_msg_id and not email:
            logging.error("INBOUND_PROCESSING:Could not extract email or message id")
            return {"success":False}, None
      
        res, err = self.message_service.reply_from_community_admin(context, {
            "title": f"Re: {subject}",
            "body": reply,
            "to": email,
            "message_id": db_msg_id,
            "from_email": from_email,
            "is_inbound": True,
            "email": email
            })

        if err:
            logging.error(f"INBOUND_PROCESSING_MESSAGE_CREATION: {str(err)}")
            return None, str(err)
    
        return {"success": True}, None
        
    except Exception as e:
        capture_message(str(e), level="error")
        logging.error(f"INBOUND_PROCESSING_EXCEPTION: {str(e)}")
        return None, MassEnergizeAPIError(e)





