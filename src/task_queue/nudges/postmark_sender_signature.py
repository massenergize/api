from _main_.utils.constants import PUBLIC_EMAIL_DOMAINS
from _main_.utils.emailer.send_email import (
    add_sender_signature,
    get_sender_signature_info,
    resend_signature_confirmation,
)
from database.models import Community, FeatureFlag


def check_and_update_signatures():
    communities = Community.objects.filter(is_published=True, is_deleted=False,postmark_contact_info__is_validated=False )
    if communities.count() == 0:
        return True
    for community in communities:
        postmark_info = community.postmark_contact_info or {}
        id = postmark_info.get("sender_signature_id")
        response = get_sender_signature_info(id)
        if response.status_code == 200:
            res = response.json()
            if res.get("Confirmed") != postmark_info.get("is_validated"):
                community.postmark_contact_info = {**postmark_info, "is_validated": res.get("Confirmed")}
                community.save()
    return True


def collect_and_create_signatures():
    communities = Community.objects.filter(is_published=True, is_deleted=False, postmark_contact_info__is_validated=False)
    if communities.count() == 0:
        return True
    for community in communities:
        email = community.owner_email
        if not email or email.split("@")[1] in PUBLIC_EMAIL_DOMAINS:
            continue
        postmark_info = community.postmark_contact_info or {}
        alias = community.sender_signature_name or community.name
        if postmark_info.get("is_nudged"):
            resend_signature_confirmation(postmark_info.get("sender_signature_id"))
        else:
            response = add_sender_signature(email, alias)
            if response.status_code != 200:
                return False
            res = response.json()
            # change is_nudge to a int of no of time a users received
            postmark_info = {
                **postmark_info,
                "is_validated": res.get("Confirmed"),
                "is_nudged": True,
                "sender_signature_id": res.get("ID"),
            }

            community.postmark_contact_info = postmark_info
            community.sender_signature_name = alias
            community.save()
    return True
