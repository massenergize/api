from django.core.mail import send_mail, EmailMessage, send_mass_mail, EmailMultiAlternatives
from _main_ import settings
from emailer.email_
def send_massenergize_email(subject, msg, to):
  ok = send_mail(
      subject,
      msg,
      settings.EMAIL_HOST_USER, #from
      [to],
      fail_silently=True,
  )

  if not ok:
    print(f"Error Occurred in Sending Email to {to}")
    return False
  return True

def send_massenergize_mass_email(subject, msg, recipient_emails):
  ok = send_mail(
      subject,
      msg,
      settings.EMAIL_HOST_USER, #from
      recipient_list=recipient_emails,
      fail_silently=True,
  )

  if not ok:
    print(f"Error occurred in sending some emails")
    return False

  print(f"{ok} sent emails")
  return True