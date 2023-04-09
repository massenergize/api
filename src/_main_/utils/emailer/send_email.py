from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sentry_sdk import capture_message
import pystmark

from _main_.settings import EMAIL_POSTMARK_SERVER_TOKEN
from _main_.utils.utils import is_test_mode

FROM_EMAIL = 'no-reply@massenergize.org'

def old_send_massenergize_email(subject, msg, to):
  if is_test_mode():
    return True


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
  if is_test_mode():
    return True

  message = pystmark.Message(
    subject=subject,
    to=to,
    sender=FROM_EMAIL, 
    text=msg, 
  )
  response = pystmark.send(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)
  response.raise_for_status()

  if not response.ok:
    capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True

def send_massenergize_email_with_attachments(temp, t_model, to, file, file_name):
  message = pystmark.Message(sender=FROM_EMAIL, to=to, template_id=temp, template_model=t_model)
  if file is not None:
    message.attach_binary(file, filename=file_name)
  response = pystmark.send_with_template(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)
  if not response.ok:
    capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True
  

def old_send_massenergize_rich_email(subject, to, massenergize_email_type, content_variables, from_email=None):
  if is_test_mode():
    return True

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
    text=text_content
  )
  response = pystmark.send(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)

  if not response.ok:
    capture_message(f"Error Occurred in Sending Email to {to}", level="error")
    return False
  return True


def old_send_massenergize_mass_email(subject, msg, recipient_emails):
  if is_test_mode():
    return True

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

def send_massenergize_mass_email(subject, msg, recipient_emails):
  if is_test_mode():
    return True

  message = pystmark.Message(
    subject=subject,
    sender=FROM_EMAIL, 
    html=msg, 
  )
  message.recipients = recipient_emails
  response = pystmark.send(message, api_key=EMAIL_POSTMARK_SERVER_TOKEN)

  if not response.ok:
    capture_message("Error occurred in sending some emails", level="error")
    return False

  return True
