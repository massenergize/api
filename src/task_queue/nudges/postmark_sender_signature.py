from _main_.utils.emailer.send_email import (
    add_sender_signature,
    get_all_sender_signatures,
    resend_signature_confirmation,
)
from database.models import Community, FeatureFlag

def check_and_update_signatures():
    communities = Community.objects.filter(is_published=True, is_deleted=False, postmark_contact_info__is_validated=False)
    response = get_all_sender_signatures(len(communities))
    if response.status_code == 200:
        res = response.json()
        signatures = res.get("Signatures", [])
        for signature in signatures:
            community = communities.filter(postmark_contact_info__sender_signature_id=signature.get("ID")).first()
            if community:
                community.postmark_contact_info = {
                    **community.postmark_contact_info,
                    "is_validated": res.get("Confirmed"),
                }
                community.save()
    return True


def collect_and_create_signatures():
    msg = f"Message for Admins"
    communities = Community.objects.filter(id=6, is_published=True, is_deleted=False)
    for community in communities:
        email = community.owner_email
        postmark_info = community.postmark_contact_info or {}
        alias = community.sender_signature_name or community.name
        if not postmark_info.get("is_validated"):
            if postmark_info.get("is_nudged"):
                response = resend_signature_confirmation(
                    postmark_info.get("sender_signature_id")
                )
            else:
                response = add_sender_signature(email, alias, msg)
                if not response.status_code == 200:
                    return False
                res = response.json()
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
