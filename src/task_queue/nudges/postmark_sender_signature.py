import traceback
from _main_.utils.constants import PUBLIC_EMAIL_DOMAINS
from _main_.utils.emailer.send_email import (
    add_sender_signature,
    get_sender_signature_info,
    resend_signature_confirmation,
)
from _main_.utils.massenergize_logger import log
from database.models import Community

def collect_and_create_signatures(task=None):
    try:
        enabled_communities = Community.objects.filter(is_published=True, is_deleted=False).exclude(
            contact_info__is_validated=False
        )
        emails= []
        for community in enabled_communities:
            email = community.owner_email
            if not email or email.split("@")[1].strip().lower() in PUBLIC_EMAIL_DOMAINS:
                continue
            postmark_info = community.contact_info or {}
            alias = community.contact_sender_alias or community.name
            if postmark_info.get("nudge_count", 0):
                id = postmark_info.get("sender_signature_id")
                response = get_sender_signature_info(id)
                if response.status_code == 200:
                    res = response.json()
                    if res.get("Confirmed"):
                        community.contact_info = {
                            **postmark_info,
                            "is_validated": res.get("Confirmed"),
                        }
                    else:
                        res = resend_signature_confirmation(
                            postmark_info.get("sender_signature_id")
                        )
                        if res.status_code == 200:
                            community.contact_info = {
                                **postmark_info,
                                "nudge_count": postmark_info.get("nudge_count", 0) + 1,
                            }
                            emails.append(email)
                        else:
                            log.error(f"ERROR Resending Confirmation to {community.name}: {res.json()} ")
                else:
                    log.error(f"ERROR getting Contact Info of {community.name}: {response.json()}")
            else:
                response = add_sender_signature(email, alias, community.owner_name, community.name)
                if response.status_code == 200:
                    res = response.json()
                    postmark_info = {
                        **postmark_info,
                        "is_validated": res.get("Confirmed"),
                        "nudge_count": 1,
                        "sender_signature_id": res.get("ID"),
                    }
                    community.contact_info = postmark_info
                    community.contact_sender_alias = alias
                
                    community.save()
                    emails.append(email)
                else:
                    log.error(f"ERROR adding signature for {community.name}: {response.json()}")

            result = {
                "scope": "CADMIN",
                "audience":",".join(emails)
            }
        return result, None
    except Exception as e:
        stack_trace = traceback.format_exc()
        log.error(f"An error occurred while collecting and creating signatures: {stack_trace}")
        return None, stack_trace
