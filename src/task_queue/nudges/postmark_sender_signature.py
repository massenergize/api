from _main_.utils.constants import PUBLIC_EMAIL_DOMAINS
from _main_.utils.emailer.send_email import (
    add_sender_signature,
    get_sender_signature_info,
    resend_signature_confirmation,
)
from database.models import Community, FeatureFlag

COMMUNITY_EMAIL_SENDER_SIGNATURE_FF = "community-email-sender-signature-feature-flag"

def collect_and_create_signatures():
    flag = FeatureFlag.objects.filter(key=COMMUNITY_EMAIL_SENDER_SIGNATURE_FF ).first()
    if not flag or not flag.enabled():
        return False
    communities = Community.objects.filter(is_published=True, is_deleted=False).exclude(contact_info__is_validated=False)
    ff_enabled_communities = flag.enabled_communities(communities)
    for community in ff_enabled_communities:
        email = community.owner_email
        if not email or email.split("@")[1] in PUBLIC_EMAIL_DOMAINS:
            continue
        postmark_info = community.contact_info or {}
        alias = community.contact_sender_alias or community.name
        if postmark_info.get("is_nudged"): 
            id = postmark_info.get("sender_signature_id")
            response = get_sender_signature_info(id)
            if response.status_code == 200:
                res = response.json()
                if res.get("Confirmed"):
                    community.contact_info = {**postmark_info, "is_validated": res.get("Confirmed")}
                    community.save()
                else:
                    resend_signature_confirmation(postmark_info.get("sender_signature_id"))
        else:
            response = add_sender_signature(email, alias, community.owner_name, community.name)
            if response.status_code == 200:
                res = response.json()
                postmark_info = {
                    **postmark_info,
                    "is_validated": res.get("Confirmed"),
                    "is_nudged": True,
                    "sender_signature_id": res.get("ID"),
                }
                community.contact_info = postmark_info
                community.contact_sender_alias = alias
                community.save()
    return True
