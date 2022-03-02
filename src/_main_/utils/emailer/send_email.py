from django.core.mail import send_mail, EmailMessage, send_mass_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sentry_sdk import capture_message
import pystmark
import requests

from _main_.settings import EMAIL_POSTMARK_SERVER_TOKEN
from _main_.settings import EMAIL_POSTMARK_API_ENDPOINT_URL

FROM_EMAIL = 'no-reply@massenergize.org'

def get_email_templates(count, offset, TemplateType=None, LayoutTemplate=None):
  request = requests.get("{}/templates".format(EMAIL_POSTMARK_API_ENDPOINT_URL),headers={
    "Accept": "application/json",
    "X-Postmark-Server-Token": EMAIL_POSTMARK_SERVER_TOKEN
  }, params={
    "Count": count,
    "Offset": offset
  })

  return request.json()

templates = get_email_templates(10, 0)

def get_template(TemplateId=None):
  request = requests.get("{}/templates".format(EMAIL_POSTMARK_API_ENDPOINT_URL),headers={
    "Accept": "application/json",
    "X-Postmark-Server-Token": EMAIL_POSTMARK_SERVER_TOKEN
  }, params={
    "TemplateId": TemplateId
  })

  return request.json()

def old_send_massenergize_email(subject, msg, to):
  ok = send_mail(
      subject,
      msg,
      FROM_EMAIL, #from
      [to],
      fail_silently=False,
  )

  if not ok:
    capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True

def send_massenergize_email(subject, msg, to):
  message = pystmark.Message(
    subject=subject,
    to=to,
    sender=FROM_EMAIL, 
    html=msg, 
  )
  response = pystmark.send(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)

  if not response.ok:
    capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    print(response.raise_for_status())
    return False
  return True


def old_send_massenergize_rich_email(subject, to, massenergize_email_type, content_variables, from_email=None):
  if not from_email:
    from_email = FROM_EMAIL
  html_content = render_to_string(massenergize_email_type, content_variables)
  text_content = strip_tags(html_content)
  msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
  msg.attach_alternative(html_content, "text/html")
  ok = msg.send(fail_silently=True)

  if not ok:
    capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True

# def send_massenergize_rich_email(subject, to, massenergize_email_type, content_variables, from_email=None):
#   if not from_email:
#     from_email = FROM_EMAIL
#   html_content = render_to_string(massenergize_email_type, content_variables)
#   text_content = strip_tags(html_content)

#   message = pystmark.Message(
#     subject=subject,
#     to=to,
#     sender=from_email, 
#     html=html_content, 
#     text=text_content
#   )
#   response = pystmark.send(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)

#   if not response.ok:
#     capture_message(f"Error Occurred in Sending Email to {to}", level="error")
#     print(response.raise_for_status())
#     return False
#   return True

def send_massenergize_rich_email(subject, to, massenergize_email_type, content_variables, from_email=None):
  if not from_email:
    from_email = FROM_EMAIL

  t_model = { # Fill out template model
    "homelink": "asdf",
    "logo": "asdf",
    "name": "asdf",
    "community": "asdf",
  }

  # TODO: Create references to all templates 
  template_id_welocme = 27142713

  message = pystmark.Message(
    to=to,
    sender=from_email, 
    template_id=template_id_welocme,
    template_model=t_model
  )

  response = pystmark.send_with_template(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)

  if not response.ok:
    capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    print(response.raise_for_status())
    return False
  return True


def old_send_massenergize_mass_email(subject, msg, recipient_emails):
  ok = send_mail(
      subject,
      msg,
      FROM_EMAIL, #from
      recipient_list=recipient_emails,
      fail_silently=True,
  )

  if not ok:
    capture_message("Error occurred in sending some emails", level="error")

    return False

  return True

def send_massenergize_mass_email(subject, msg, to):
  message = pystmark.Message(
    subject=subject,
    to=to,
    sender=FROM_EMAIL, 
    html=msg, 
  )
  response = pystmark.send(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)

  if not response.ok:
    capture_message("Error occurred in sending some emails", level="error")
    print(response.raise_for_status())
    return False

  return True


get_email_templates()