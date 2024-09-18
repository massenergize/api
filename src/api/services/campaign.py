from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from _main_.utils.context import Context
from api.store.campaign import CampaignStore
from api.utils.filter_functions import sort_items
from _main_.utils.massenergize_logger import log
from typing import Tuple

from apps__campaigns.helpers import generate_analytics_data, get_campaign_details, get_campaign_technology_details

from apps__campaigns.helpers import get_campaign_details_for_user

from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments

from api.utils.constants import CAMPAIGN_MANAGER_INVITE_EMAIL_TEMPLATE

from _main_.utils.constants import CAMPAIGN_URL_ROOT


class CampaignService:
    """
  Service Layer for all the campaigns
  """

    def __init__(self):
        self.store = CampaignStore()

    def get_campaign_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign, err = self.store.get_campaign_info(context, args)
        if err:
            return None, err
        ser_cam = serialize(campaign, full=True)
        other_details = get_campaign_details(campaign.id, True)
        result = {**ser_cam, **other_details, "stats": generate_analytics_data(campaign.id)}

        return result, None

    def get_campaign_info_for_user(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        email = args.get("email", None)
        campaign, err = self.store.get_campaign_info(context, args)
        if err:
            return None, err
        ser_cam = serialize(campaign, full=True)
        other_details = get_campaign_details_for_user(campaign, email)
        result = {**ser_cam, **other_details}

        return result, None

    def list_campaigns(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        campaigns, err = self.store.list_campaigns(context, args)
        if err:
            return None, err
        return serialize_all(campaigns), None

    def create_campaign(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign, err = self.store.create_campaign(context, args)
            if err:
                return None, err
            return serialize(campaign), None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def create_campaign_from_template(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            campaign, err = self.store.create_campaign_from_template(context, args)
            if err:
                return None, err
            ser_cam = serialize(campaign, full=True)
            other_details = get_campaign_details(campaign.id, True)
            result = {**ser_cam, **other_details, "stats": generate_analytics_data(campaign.id)}

            return result, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_campaign(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign, err = self.store.update_campaigns(context, args)
        if err:
            return None, err
        return serialize(campaign), None

    def delete_campaign(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign, err = self.store.delete_campaign(context, args)
        if err:
            return None, err
        return serialize(campaign), None

    def list_campaigns_for_admins(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        campaigns, err = self.store.list_campaigns_for_admins(context, args)
        if err:
            return None, err
        sorted = sort_items(campaigns, context.get_params())
        return paginate(sorted, context.get_pagination_data()), None

    def add_campaign_manager(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_manager(context, args)
        if err:
            return None, err
        data = {
            "campaign_name": res.campaign.title,
            "email": res.user.email,
            "url": f'{CAMPAIGN_URL_ROOT}/admin/campaign/{res.campaign.slug}/edit',
            "name": res.user.full_name,
        }
        send_massenergize_email_with_attachments(
            CAMPAIGN_MANAGER_INVITE_EMAIL_TEMPLATE, data, [res.user.email], None, None
        )

        return serialize(res, full=True), None

    def remove_campaign_manager(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign_manager, err = self.store.remove_campaign_manager(context, args)
        if err:
            return None, err
        return serialize(campaign_manager, full=True), None

    def update_campaign_manager(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign_manager, err = self.store.update_campaign_manager(context, args)
        if err:
            return None, err
        return serialize(campaign_manager, full=True), None

    def add_campaign_community(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_community(context, args)
        if err:
            return None, err
        return res, None

    def remove_campaign_community(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.remove_campaign_community(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def update_campaign_community(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.update_campaign_community(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def add_campaign_technology(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_technology(context, args)
        if err:
            return None, err
        return serialize_all(res, full=True), None

    def update_campaign_technology(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.update_campaign_technology(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def remove_campaign_technology(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.remove_campaign_technology(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def create_campaign_technology_testimonial(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.create_campaign_technology_testimonial(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def update_campaign_technology_testimonial(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.update_campaign_technology_testimonial(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def create_campaign_technology_comment(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        is_from_admin_site = args.get("is_from_admin_site", False)

        res, err = self.store.create_campaign_technology_comment(context, args)
        if err:
            return None, err
        if is_from_admin_site:
            return serialize(res), None
        return serialize_all(res, full=True), None

    def update_campaign_technology_comment(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.update_campaign_technology_comment(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def list_campaign_technology_comments(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_technology_comments(context, args)
        if err:
            return None, err
        return serialize_all(res), None

    def list_campaign_technology_testimonials(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_technology_testimonials(context, args)
        if err:
            return None, err
        return serialize_all(res), None

    def list_campaign_managers(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_managers(context, args)
        if err:
            return None, err
        return serialize_all(res), None

    def list_campaign_communities(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_communities(context, args)
        if err:
            return None, err
        return serialize_all(res), None

    def list_campaign_technologies(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_technologies(context, args)
        if err:
            return None, err
        return serialize_all(res), None

    def list_campaign_technology_event(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_technology_event(context, args)
        if err:
            return None, err
        return serialize_all(res, full=True), None

    def add_campaign_partners(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_partners(context, args)
        if err:
            return None, err
        return res, None

    def remove_campaign_partners(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.remove_campaign_partners(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def add_campaign_technology_event(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_technology_event(context, args)
        if err:
            return None, err
        return res, None

    def generate_campaign_links(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.generate_campaign_link(context, args)
        if err:
            return None, err
        return res, None

    def campaign_link_visits_count(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.campaign_link_visits_count(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def add_campaign_follower(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_follower(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def add_campaign_technology_follower(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_technology_follower(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def add_campaign_technology_view(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_technology_view(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def add_campaign_technology_like(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_technology_like(context, args)
        if err:
            return None, err

        return res, None

    def delete_campaign_technology_testimonial(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.delete_campaign_technology_testimonial(context, args)
        if err:
            return None, err

        return serialize(res, full=True), None

    def get_campaign_analytics(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.get_campaign_analytics(context, args)
        if err:
            return None, err

        return res, None

    def add_campaign_like(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_like(context, args)
        if err:
            return None, err

        return serialize(res), None

    def transfer_ownership(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.transfer_ownership(context, args)
        if err:
            return None, err

        return res, None

    def get_campaign_technology_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        email = args.get("email", context.user_email)
        res, err = self.store.get_campaign_technology_info(context, args)
        if err:
            return None, err

        ser = serialize(res, full=True)

        other_details = get_campaign_technology_details({"campaign_technology_id": res.id, 'email': email})
        result = {**ser, **other_details}

        return result, None

    def get_campaign_technology_testimonial(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.get_campaign_technology_testimonial(context, args)
        if err:
            return None, err

        return serialize(res, full=True), None

    def create_campaign_config(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.create_campaign_config(context, args)
        if err:
            return None, err

        return serialize(res, full=True), None

    def update_campaign_config(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.update_campaign_config(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def get_campaign_config(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.get_campaign_config(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def create_campaign_navigation(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.create_campaign_navigation(context, args)
        if err:
            return None, err
        return serialize(res, full=True), None

    def track_activity(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.track_activity(context, args)
        if err:
            return None, err

        return serialize(res), None

    def add_campaign_view(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_view(context, args)
        if err:
            return None, err

        return serialize(res), None

    def delete_campaign_technology_comment(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.delete_campaign_technology_comment(context, args)
        if err:
            return None, err

        return serialize_all(res, full=True), None

    def create_campaign_technology(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.create_campaign_technology(context, args)
        if err:
            return None, err

        return serialize(res, full=True), None

    def list_campaign_communities_events(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_communities_events(context, args)
        if err:
            return None, err
        return res, None

    def list_campaign_communities_testimonials(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_communities_testimonials(context, args)
        if err:
            return None, err
        return res, None

    def list_campaign_communities_vendors(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.list_campaign_communities_vendors(context, args)
        if err:
            return None, err

        return serialize_all(res), None

    def add_campaign_technology_testimonial(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.add_campaign_technology_testimonial(context, args)
        if err:
            return None, err

        return res, None

    def remove_campaign_technology_event(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.remove_campaign_technology_event(context, args)
        if err:
            return None, err

        return serialize(res, full=True), None

    def update_campaign_key_contact(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.update_campaign_key_contact(context, args)
        if err:
            return None, err

        return serialize_all(res, full=True), None
    
    def delete_call_to_action(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        res, err = self.store.delete_call_to_action(context, args)
        if err:
            return None, err

        return serialize(res), None
