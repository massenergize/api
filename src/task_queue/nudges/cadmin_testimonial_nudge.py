from datetime import datetime
import traceback
from _main_.utils.common import encode_data_for_URL, serialize_all
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT, ME_LOGO_PNG
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.feature_flag_keys import TESTIMONIAL_AUTO_SHARE_SETTINGS_NUDGE_FEATURE_FLAG_KEY
from _main_.utils.massenergize_logger import log
from api.utils.api_utils import generate_email_tag, get_sender_email
from api.utils.constants import CADMIN_TESTIMONIAL_NUDGE_TEMPLATE
from database.models import Community, CommunityAdminGroup, FeatureFlag, Testimonial
from task_queue.helpers import get_summary
from task_queue.nudges.nudge_utils import get_admin_email_list, update_last_notification_dates
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.utils import timezone

from task_queue.type_constants import CADMIN_TESTIMONIALS_NUDGE


TESTIMONIAL_NUDGE_KEY = "cadmin_testimonial_nudge"
	
def get_cadmin_names_and_emails(community):
	"""
	Get all the community admin names and emails
	"""
	if not community:
		log.error("Community is None in get_cadmin_names_and_emails")
		return {}
		
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
			if not email:  # Skip if email is None
				log.warning(f"Skipping admin with no email in community {community.name}")
				continue
				
			name_emails[email] = {
				"name": name,
				"preferences": preferences,
				"nudge_dates": nudge_dates,
				"user_info": user_info
			}
			
	except Exception as e:
		log.exception(e)
		return {}
		
	return name_emails

def format_date(date_str):
	if not date_str:
		return "N/A"
	try:
		return date_str.strftime("%B %d, %Y")
	except Exception as e:
		log.error(f"Error formatting date: {str(e)}")
		return "N/A"



	
def send_nudge(data, community, admin):
	"""
		Send a nudge to the community admin to approve testimonials
	"""
	if not data or not community or not admin:
		log.error("Missing required data for send_nudge")
		return False, "Missing required data"
		
	try:		
		email = admin.get("email")
		name = admin.get("name")
		user_info = admin.get("user_info")

		if not email:
			log.error("No email provided for admin")
			return False, "No email provided"

		serialized_data = serialize_all(data)
		to_send = [
			{
				"title": testimonial.get('title'),
				"body": get_summary(testimonial.get('body', ""), 50),
				"preferred_name": testimonial.get('preferred_name') or testimonial.get('user', {}).get('full_name', "Anonymous") if testimonial else "Anonymous",
				"community": testimonial.get("community", {}).get("name"),
				"view_url": f"{COMMUNITY_URL_ROOT}/{community.subdomain}/testimonials/{testimonial.get('id')}",
				"date": format_date(testimonial.get('published_at')),
				"image": {"url": testimonial.get('image', {}).get('url', None)} if testimonial.get('image') else None,
			} for testimonial in serialized_data
		]
		data = {
			"testimonials": to_send,
			"community_name": community.name,
			"community_logo": community.logo.file.url if community.logo else ME_LOGO_PNG,
			"name": name,
		}
		login_method = user_info.get("login_method") if user_info else None
		cred = encode_data_for_URL({"email": email, "login_method": login_method})
		data["change_preference_link"] = f"{ADMIN_URL_ROOT}/admin/profile/preferences/?cred={cred}"

		tag = generate_email_tag(community.subdomain, CADMIN_TESTIMONIALS_NUDGE)
		 
		ok, err = send_massenergize_email_with_attachments(CADMIN_TESTIMONIAL_NUDGE_TEMPLATE, data, [email], None, None, get_sender_email(community.id), tag)

		if err:
			log.error(f"Failed to send Cadmin Nudge to '{email}' || ERROR: {err}")
			return None, err
					
		return True, None
	except Exception as e:
		log.exception(e)
		return False, e
	


def get_admin_testimonials(notification_dates, testimonial_list):
	if not testimonial_list:
		log.warning("No testimonial list provided")
		return []
		
	try:
		today = timezone.now()
		a_week_ago = today - relativedelta(weeks=4)

		user_event_nudge = notification_dates.get(TESTIMONIAL_NUDGE_KEY, None) if notification_dates else None

		if not user_event_nudge or not notification_dates:
			return testimonial_list.filter(Q(published_at__range=[a_week_ago, today])).order_by('published_at')
		
		try:
			last_received_at = datetime.strptime(user_event_nudge, '%Y-%m-%d')
			date_aware = timezone.make_aware(last_received_at, timezone=timezone.get_default_timezone())
			last_time = date_aware if date_aware else a_week_ago
		except Exception as e:
			log.error(f"Error parsing date {user_event_nudge}: {str(e)}")
			last_time = a_week_ago

		return testimonial_list.filter(Q(published_at__range=[last_time, today])).order_by('published_at')
	except Exception as e:
		log.exception(e)
		return []

	
def prepare_testimonials_for_community_admins(task=None):
	"""
	Prepare a list of testimonials that are pending approval for each community admin
	"""
	try:
        
		flag = FeatureFlag.objects.get(key=TESTIMONIAL_AUTO_SHARE_SETTINGS_NUDGE_FEATURE_FLAG_KEY)
		if not flag or not flag.enabled():
			log.info("Feature flag not enabled for testimonial nudge")
			return None, "Feature flag not enabled"

		communities = Community.objects.filter(is_published=True, is_deleted=False)
		if not communities.exists():
			log.info("No published communities found")
			return None, "No published communities found"
			
		communities = flag.enabled_communities(communities)
		if not communities.exists():
			log.info("No communities enabled for testimonial nudge")
			return None, "No communities enabled for testimonial nudge"
			
		emailed_list = []
		failures = {}

		for community in communities:
			try:
				log.info(f"*** Processing Testimonial Auto-Share Nudge for {community.name}")
				testimonials_auto_shared = community.testimonial_shares.filter(testimonial__is_published=True)

				if not testimonials_auto_shared.exists():
					log.info(f"No testimonials found for community {community.name}")
					continue
				
				list_to_send = [t.testimonial for t in testimonials_auto_shared if t.testimonial]

				if not list_to_send:
					log.info(f"No valid testimonials to send for community {community.name}")
					continue

				testimonials = Testimonial.objects.filter(id__in=[t.id for t in list_to_send]).order_by('published_at')
				if not testimonials.exists():
					log.info(f"No testimonials found in database for community {community.name}")
					continue
			
				all_admins = get_cadmin_names_and_emails(community)
				if not all_admins:
					log.info(f"No community admins found for community {community.name}")
					continue

				admins_to_receive = get_admin_email_list(all_admins, TESTIMONIAL_NUDGE_KEY)
				if not admins_to_receive:
					log.info(f"No admins to receive nudge for community {community.name}")
					continue

				for email, data in admins_to_receive.items():
					if not email or not data:
						continue
						
					name = data.get("name")
					nudge_dates = data.get("nudge_dates")
					user_info = data.get("user_info")
					
					admin_testimonials = get_admin_testimonials(nudge_dates, testimonials)
					if not admin_testimonials:
						continue
			        
					log.info(f"*** Sending Testimonial({len(admin_testimonials)}) Nudge to {email}")
					ok, err = send_nudge(admin_testimonials, community, {"name": name, "email": email, "user_info": user_info})
					if not ok:
						log.error(f"Failed to send nudge to community admin {email} for community {community.name}: {err}")
						failures[email] = str(err)
						continue
						
				emailed_list.append(email)
				
			except Exception as e:
				log.exception(f"Error processing community {community.name}: {str(e)}")
				continue

		update_last_notification_dates(emailed_list, TESTIMONIAL_NUDGE_KEY)

		if len(emailed_list)==0:
			result = {"audience": ",".join(emailed_list), "scope": "USER", "failures": failures}
			return None, str(result)

	
		res = {"scope":"CADMIN","audience": ",".join(emailed_list), "failures": failures}
		log.info("Successfully sent nudge to all community admins")
		return res, None
	except Exception as e:
		stack_trace = traceback.format_exc()
		log.error(f"Community admin nudge exception: {stack_trace}")
		return None, stack_trace