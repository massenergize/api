from django.core.mail import send_mail, EmailMessage, send_mass_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sentry_sdk import capture_message
import pystmark

from _main_.settings import EMAIL_POSTMARK_SERVER_TOKEN

FROM_EMAIL = 'no-reply@massenergize.org'

def send_massenergize_email(subject, msg, to):
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

def send_massenergize_rich_email(subject, to, massenergize_email_type, content_variables, from_email=None):
  if not from_email:
    from_email = FROM_EMAIL
  html_content = render_to_string(massenergize_email_type, content_variables)
  text_content = strip_tags(html_content)

  message = pystmark.Message(
    subject=subject,
    to=to,
    sender=from_email, 
    html=html_content, 
    text=text_content
  )
  response = pystmark.send(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)

  if not response.ok:
    capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True


def send_massenergize_mass_email(subject, msg, recipient_emails):
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
