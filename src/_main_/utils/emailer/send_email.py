import logging
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
from _main_.utils.massenergize_logger import log
import pystmark

from _main_.settings import POSTMARK_ACCOUNT_TOKEN, POSTMARK_EMAIL_SERVER_TOKEN, POSTMARK_DOWNLOAD_SERVER_TOKEN, IS_PROD
from _main_.utils.constants import ME_INBOUND_EMAIL_ADDRESS
from _main_.utils.utils import is_test_mode, run_in_background

FROM_EMAIL = 'no-reply@massenergize.org'

def is_dev_env():
  if IS_PROD:
    return False
  else:
    return True

@run_in_background
def send_massenergize_email(subject, msg, to, sender=None):
  if is_test_mode(): 
    return True

  message = pystmark.Message(
    subject=subject,
    to=to,
    sender=sender or FROM_EMAIL, 
    text=msg, 
  )
  response = pystmark.send(message, api_key=POSTMARK_EMAIL_SERVER_TOKEN)
  response.raise_for_status()

  if not response.ok:
    log.error(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True

def send_massenergize_email_with_attachments(temp, t_model, to, file, file_name, sender=None, tag=None):
  if is_test_mode():
    return True
  t_model = {**t_model, "is_dev":is_dev_env()}

  
  message = pystmark.Message(sender=sender or FROM_EMAIL, to=to, template_alias=temp, template_model=t_model, tag=tag)
  # postmark server can be Production, Development or Testing (for local testing)
  postmark_server = POSTMARK_EMAIL_SERVER_TOKEN
  if file is not None:
    message.attach_binary(file, filename=file_name)
    # downloads or any message with attachments may have a different server since Testing server doesn't process attachments
    if POSTMARK_DOWNLOAD_SERVER_TOKEN:
      postmark_server = POSTMARK_DOWNLOAD_SERVER_TOKEN
  response = pystmark.send_with_template(message, api_key=postmark_server)
  if not response.ok:
    logging.error("EMAILING_ERROR: "+str(response.json()))
    #if IS_PROD:
    #  log.error(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True
  
@run_in_background
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
    log.error(f"Error Occurred in Sending Email to {to}", level="error")
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
    #  log.error("Error occurred in sending some emails", level="error")
    return False

  return True





def add_sender_signature(email, alias, first_name, community):
  if is_test_mode():
    return True
  if not first_name:
    first_name = "Admin"
  url = "https://api.postmarkapp.com/senders"
  headers = {"Accept": "application/json","Content-Type": "application/json","X-Postmark-Account-Token": POSTMARK_ACCOUNT_TOKEN}
  msg = f'Dear {first_name} - as the community contact for {community}, we need you to validate your email as a valid email address. Please select "confirm sender signature" to continue. If you have questions about this, feel free to contact Support@MassEnergize.org. Thank you! \n Aimee, Kaat and Brad from the MassEnergize platform team.'
  data = {
      "FromEmail": email,
      "Name": alias,
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



def get_sender_signature_info(signature_id):
  if is_test_mode():
    return True
  url = f"https://api.postmarkapp.com/senders/{signature_id}"
  headers = {"Accept": "application/json","X-Postmark-Account-Token": POSTMARK_ACCOUNT_TOKEN}
  response = requests.get(url, headers=headers)
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