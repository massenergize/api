from _main_.utils.common import encode_data_for_URL, parse_datetime_to_aware, serialize_all
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.massenergize_logger import log
from api.store.testimonial import get_auto_shared_with_list
from api.utils.api_utils import get_sender_email
from api.utils.constants import CADMIN_TESTIMONIAL_NUDGE_TEMPLATE
from database.models import Community, CommunityAdminGroup
from task_queue.helpers import get_summary


class TestimonialApprovalNudge:
	def __init__(self):
		self.communities = Community.objects.filter(is_deleted=False, is_published=True)
	
	def get_cadmin_names_and_emails(self, community):
		"""
		Get all the community admin names and emails
		"""
		name_emails = {}
		try:
			c = (CommunityAdminGroup.objects.filter(community=community)
				.values_list('members__full_name', 'members__email', "members__user_info")
			)
			
			for (name, email, user_info) in list(c):
				name_emails[email] = (name, user_info)
				
		except Exception as e:
			log.exception(str(e))
			
		return name_emails
	
	def send_nudge(self, data, community):
		"""
			Send a nudge to the community admin to approve testimonials
		"""
		try:
			admins = self.get_cadmin_names_and_emails(community)
			
			serialized_data = serialize_all(data)
			to_send = [
				{
					"title": testimonial.get('title'),
					"body": get_summary(testimonial.get('body', ""), 50),
					"preferred_name": testimonial.get('preferred_name') or testimonial.get('user', {}).get('full_name', "Anonymous") if testimonial else "Anonymous",
					"community": testimonial.get("community", {}).get("name"),
					"view_url": f"{COMMUNITY_URL_ROOT}/{community.subdomain}/testimonials/{testimonial.get('id')}",
					"date": testimonial.get('published_at').strftime("%B %d, %Y")
				} for testimonial in serialized_data
			]
			data = {"testimonials": to_send, "community_name": community.name}
			
			from_email = get_sender_email(community.id)
			
			for email, (name, user_info) in admins.items():
				data["name"] = name
				login_method = user_info.get("login_method") if user_info else None
				cred = encode_data_for_URL({"email": email, "login_method": login_method})
				data["change_preference_link"] = f"{ADMIN_URL_ROOT}/admin/profile/preferences/?cred={cred}"
				send_massenergize_email_with_attachments(CADMIN_TESTIMONIAL_NUDGE_TEMPLATE, data, [email], None, None, from_email)
			
			return True
		except Exception as e:
			log.exception(str(e))
			return False
	
	def prepare_testimonials_for_community_admins(self):
		"""
		Prepare a list of testimonials that are pending approval for each community admin
		"""
		try:
			today = parse_datetime_to_aware()
			for community in self.communities:
				
				testimonials_auto_shared = get_auto_shared_with_list([community.id])
				if not testimonials_auto_shared:
					continue
				
				list_to_send = testimonials_auto_shared.filter(is_published=True, published_at__date=today)
				if not list_to_send:
					continue
				
				ok = self.send_nudge(list_to_send, community)
				if not ok:
					log.error(f"Failed to send nudge to community admin for community {community.name}")
			
			log.info("Successfully sent nudge to all community admins")
			return True
		except Exception as e:
			log.exception(str(e))
			return False
