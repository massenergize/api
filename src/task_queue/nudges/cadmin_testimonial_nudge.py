from datetime import datetime
from _main_.utils.common import encode_data_for_URL, serialize_all
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.feature_flag_keys import TESTIMONIAL_AUTO_SHARE_SETTINGS_NUDGE_FEATURE_FLAG_KEY
from _main_.utils.massenergize_logger import log
from api.utils.api_utils import get_sender_email
from api.utils.constants import CADMIN_TESTIMONIAL_NUDGE_TEMPLATE
from database.models import Community, CommunityAdminGroup, FeatureFlag, Testimonial
from task_queue.helpers import get_summary
from task_queue.nudges.nudge_utils import ME_DEFAULT_IMAGE, get_admin_email_list, update_last_notification_dates
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.utils import timezone


TESTIMONIAL_NUDGE_KEY = "cadmin_testimonial_nudge"
	
def get_cadmin_names_and_emails(community):
	"""
	Get all the community admin names and emails
	"""
	name_emails = {}
	try:
		c = (CommunityAdminGroup.objects.filter(community=community)
			.values_list(
				'members__full_name',
				'members__email', 
				"members__user_info", 
				'members__preferences',  
				"members__notification_dates"
			)
		)
		
		for (name, email, user_info, preferences, nudge_dates) in list(c):
			name_emails[email] = {
				"name": name,
				"preferences": preferences,
				"nudge_dates": nudge_dates,
				"user_info": user_info
			}
			
	except Exception as e:
		log.exception(e)
		return None
		
	return name_emails



	
def send_nudge(data, community, admin):
	"""
		Send a nudge to the community admin to approve testimonials
	"""
	try:		
		email = admin.get("email")
		name = admin.get("name")
		user_info = admin.get("user_info")

		serialized_data = serialize_all(data)
		to_send = [
			{
				"title": testimonial.get('title'),
				"body": get_summary(testimonial.get('body', ""), 50),
				"preferred_name": testimonial.get('preferred_name') or testimonial.get('user', {}).get('full_name', "Anonymous") if testimonial else "Anonymous",
				"community": testimonial.get("community", {}).get("name"),
				"view_url": f"{COMMUNITY_URL_ROOT}/{community.subdomain}/testimonials/{testimonial.get('id')}",
				"date": testimonial.get('published_at').strftime("%B %d, %Y"),
				"image": {"url": testimonial.get('image', {}).get('url', None)} if testimonial.get('image') else None,
			} for testimonial in serialized_data
		]
		data = {
			"testimonials": to_send,
			"community_name": community.name,
			"community_logo": community.logo.file.url if community.logo else ME_DEFAULT_IMAGE,
			"name": name,
		}
		login_method = user_info.get("login_method") if user_info else None
		cred = encode_data_for_URL({"email": email, "login_method": login_method})
		data["change_preference_link"] = f"{ADMIN_URL_ROOT}/admin/profile/preferences/?cred={cred}"
		 
		send_massenergize_email_with_attachments(CADMIN_TESTIMONIAL_NUDGE_TEMPLATE, data, [email], None, None, get_sender_email(community.id))

					
		return True
	except Exception as e:
		log.exception(e)
		return False
	


def get_admin_testimonials(notification_dates, testimonial_list):
	today = timezone.now()
	a_week_ago = today - relativedelta(weeks=4)

	user_event_nudge = notification_dates.get(TESTIMONIAL_NUDGE_KEY, None)

	if not user_event_nudge or not notification_dates:
		return testimonial_list.filter(Q(published_at__range=[a_week_ago, today])).order_by('published_at')
	
	last_received_at = datetime.strptime(user_event_nudge, '%Y-%m-%d')
	date_aware = timezone.make_aware(last_received_at, timezone=timezone.get_default_timezone())

	last_time = date_aware if date_aware else a_week_ago

	return testimonial_list.filter(Q(published_at__range=[last_time, today])).order_by('published_at')

	
def prepare_testimonials_for_community_admins(task=None):
	"""
	Prepare a list of testimonials that are pending approval for each community admin
	"""
	try:
        
		flag = FeatureFlag.objects.get(key=TESTIMONIAL_AUTO_SHARE_SETTINGS_NUDGE_FEATURE_FLAG_KEY)
		if not flag or not flag.enabled():
			return False

		communities = Community.objects.filter(is_published=True, is_deleted=False)
		communities = flag.enabled_communities(communities)

		for community in communities:
			testimonials_auto_shared = community.testimonial_shares.filter(testimonial__is_published=True)

			if not testimonials_auto_shared:
				continue
			
			list_to_send = [t.testimonial for t in testimonials_auto_shared]

			testimonials = Testimonial.objects.filter(id__in=[t.id for t in list_to_send]).order_by('published_at')
		
			all_admins = get_cadmin_names_and_emails(community)

			if not all_admins:
				log.info(f"No community admins found for community {community.name}")
				continue

			admins_to_receive = get_admin_email_list(all_admins, TESTIMONIAL_NUDGE_KEY)

			for email, data in admins_to_receive.items():
				name = data.get("name")
				nudge_dates = data.get("nudge_dates")
				user_info = data.get("user_info")
				admin_testimonials = get_admin_testimonials(nudge_dates, testimonials)
				if not admin_testimonials:
					continue
		
				ok = send_nudge(admin_testimonials, community, {"name": name, "email": email, "user_info": user_info})
				if not ok:
					log.error(f"Failed to send nudge to community admin for community {community.name}")

			update_last_notification_dates(admins_to_receive.keys(), TESTIMONIAL_NUDGE_KEY)

		log.info("Successfully sent nudge to all community admins")
		return True
	except Exception as e:
		log.exception(e)
		return False