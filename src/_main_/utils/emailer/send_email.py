from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
from sentry_sdk import capture_message
import pystmark

from _main_.settings import IS_CANARY, POSTMARK_ACCOUNT_TOKEN, POSTMARK_EMAIL_SERVER_TOKEN, POSTMARK_DOWNLOAD_SERVER_TOKEN, IS_PROD
from _main_.utils.constants import ME_INBOUND_EMAIL_ADDRESS
from _main_.utils.utils import is_test_mode

FROM_EMAIL = 'no-reply@massenergize.org'

def is_dev_env():
  if IS_PROD:
    return False
  else:
    return True


def send_massenergize_email(subject, msg, to):
  if is_test_mode(): 
    return True

  message = pystmark.Message(
    subject=subject,
    to=to,
    sender=FROM_EMAIL, 
    text=msg, 
  )
  response = pystmark.send(message, api_key=POSTMARK_EMAIL_SERVER_TOKEN)
  response.raise_for_status()

  if not response.ok:
    #if IS_PROD:
    #  capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True

def send_massenergize_email_with_attachments(temp, t_model, to, file, file_name):
  if is_test_mode():
    return True
  t_model = {**t_model, "is_dev":is_dev_env()}

  
  message = pystmark.Message(sender=FROM_EMAIL, to=to, template_alias=temp, template_model=t_model)
  # postmark server can be Production, Development or Testing (for local testing)
  postmark_server = POSTMARK_EMAIL_SERVER_TOKEN
  if file is not None:
    message.attach_binary(file, filename=file_name)
    # downloads or any message with attachments may have a different server since Testing server doesn't process attachments
    if POSTMARK_DOWNLOAD_SERVER_TOKEN:
      postmark_server = POSTMARK_DOWNLOAD_SERVER_TOKEN
  response = pystmark.send_with_template(message, api_key=postmark_server)
  if not response.ok:
    #if IS_PROD:
    #  capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True
  
def send_massenergize_rich_email(subject, to, massenergize_email_type, content_variables, from_email=None):
  if is_test_mode():
    return True
  
  if not from_email:
    from_email = FROM_EMAIL
  html_content = render_to_string(massenergize_email_type, content_variables)
  text_content = strip_tags(html_content)

  message = pystmark.Message(
    subject=subject,
    to=to,
    sender=from_email, 
    html=html_content, 
    text=text_content,
    reply_to=ME_INBOUND_EMAIL_ADDRESS,
  )
  response = pystmark.send(message, api_key=POSTMARK_EMAIL_SERVER_TOKEN)

  if not response.ok:
    #if IS_PROD:
    #  capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True

def send_massenergize_mass_email(subject, msg, recipient_emails):
  if is_test_mode():
    return True

  message = pystmark.Message(
    subject=subject,
    sender=FROM_EMAIL, 
    html=msg, 
  )
  message.recipients = recipient_emails
  response = pystmark.send(message, api_key=POSTMARK_EMAIL_SERVER_TOKEN)

  if not response.ok:
    #if IS_PROD:
    #  capture_message("Error occurred in sending some emails", level="error")
    return False

  return True





def add_sender_signature(email, name):
  if is_test_mode():
    return True
  url = "https://api.postmarkapp.com/senders"
  headers = {"Accept": "application/json","Content-Type": "application/json","X-Postmark-Account-Token": POSTMARK_ACCOUNT_TOKEN}
  msg = f"Dear Admin,\n As part of the new development to improve communication and trust between community and its members"
  data = {
      "FromEmail": email,
      "Name": name,
      "ReplyToEmail":email,
      "ConfirmationPersonalNote": msg
  }

  response = requests.post(url, headers=headers, json=data)

  return response


def resend_signature_confirmation(signature_id):
  if is_test_mode():
    return True
  url = f"https://api.postmarkapp.com/senders/{signature_id}/resend"
  headers = {"Accept": "application/json","Content-Type": "application/json","X-Postmark-Account-Token":POSTMARK_ACCOUNT_TOKEN }
  response = requests.post(url, headers=headers)
  return response



def get_all_sender_signatures(count=100):
  if is_test_mode():
    return True
  url = f"https://api.postmarkapp.com/senders"
  headers = {"Accept": "application/json","X-Postmark-Account-Token": POSTMARK_ACCOUNT_TOKEN}
  params = {"count": count,"offset": 0}
  response = requests.get(url, headers=headers, params=params)
  return response



def update_sender_signature(signature_id, name):
  if is_test_mode():
    return True
  url = f"https://api.postmarkapp.com/senders/{signature_id}"
  headers = {"Accept": "application/json","Content-Type": "application/json","X-Postmark-Account-Token": POSTMARK_ACCOUNT_TOKEN}
  data = {
  "Name":name,
}
  response = requests.put(url, headers=headers, json=data)
  return response