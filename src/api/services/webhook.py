from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.context import Context
from typing import Tuple
from api.tasks import deactivate_user
from api.utils.constants import GUEST_USER

from database.models import UserProfile
import re
import urllib.parse

ONE_DAY = 60*60*24
HARD_BOUNCE="HardBounce"
WELCOME_MESSAGE="Welcome Message From MassEnergize"



def extract_email_content(text):
  subject_match = re.search(r"Subject: (.+)\n", text)
  if subject_match:
      subject = subject_match.group(1)
  else:
      subject = None

  message_match = re.search(r"\*(.+?)\*", text, re.DOTALL)
  if message_match:
      message = message_match.group(1)
  else:
     message = None

  return subject,message


def extract_msg_id(text):
    link = text.strip().split("and respond to message\n")
    link = link[1].strip()
    url_match = re.search(r'<(.*?)>', link)
    url = url_match.group(1)
    if url:
      parsed_url = urllib.parse.urlparse(url)
      path = parsed_url.path
      path = urllib.parse.unquote(path)
      id = path.split("/")
      return id[5]
    return None
       

   

class WebhookService:
  """
  Service Layer for all the webhooks
  """

  def __init__(self):
    pass

  def bounce_email_webhook(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    email = args.get("Email")
    bounce_type = args.get("Type")
    email_subject = args.get("Subject")

    if bounce_type == HARD_BOUNCE and email_subject == WELCOME_MESSAGE:
        user = UserProfile.objects.filter(email=email).first()
        if user:
            user_info = user.user_info.get("user_type")
            if user_info == GUEST_USER:
                deactivate_user.apply_async((user.email,),countdown=ONE_DAY)

    return {"success":True}, None
  
  def process_inbound_webhook(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:

    reply = args.get("StrippedTextReply")
    text_body = args.get("TextBody")

    splitted_body = text_body.strip().split("Here is a copy of the message:")
    user_msg_content = splitted_body[1].strip().split("If possible, please reply through the admin portal rather than")[0].strip()
    subject, message = extract_email_content(user_msg_content)

    db_msg_id = extract_msg_id(splitted_body[0])
    # if email and message:
    #    email= re.search(r"\(([^)]+)\)", email)
    #    email = email.group(1)


      # save reply to db
      #  send user a reply to the email

    


    return {"success":True}, None 
    pass



