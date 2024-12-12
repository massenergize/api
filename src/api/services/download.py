from _main_.utils.massenergize_errors import MassEnergizeAPIError
from api.constants import ACTION_USERS, ACTIONS, CAMPAIGN_INTERACTION_PERFORMANCE_REPORT, CAMPAIGN_PERFORMANCE_REPORT, CAMPAIGN_VIEWS_PERFORMANCE_REPORT, COMMUNITIES, FOLLOWED_REPORT, LIKE_REPORT, LINK_PERFORMANCE_REPORT, METRICS, POSTMARK_NUDGE_REPORT, SAMPLE_USER_REPORT, TEAMS, USERS, CADMIN_REPORT, SADMIN_REPORT, COMMUNITY_PAGEMAP
from api.store.download import DownloadStore
from _main_.utils.context import Context
from typing import Tuple
from api.tasks import download_data
from api.constants import DOWNLOAD_POLICY


class DownloadService:

    def __init__(self):
        self.store = DownloadStore()

    def users_download(self, context: Context, community_id=None, team_id=None) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'team_id': team_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, USERS)
        return [], None

    def actions_download(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, ACTIONS)
        return [], None

    def communities_download(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin': context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, COMMUNITIES)
        return [], None

    def teams_download(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin': context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, TEAMS)
        return [], None

    def metrics_download(self, context: Context, args, community_id, audience, report_community_ids) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin': context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in,
            'audience': audience,
            'community_ids': report_community_ids,
        }
        download_data.delay(data, METRICS)
        return [], None

    # these two routines don't do what they should do, which is to send a copy of the nudge report to cadmins or sadmins
    
    def send_cadmin_report(self, context: Context, community_id=None) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, CADMIN_REPORT)
        return [], None
    
    def download_postmark_nudge_report(self, context: Context, community_id=None, period=45) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in,
            "period":period

        }
        download_data.delay(data, POSTMARK_NUDGE_REPORT)
        return [], None
    
    def send_sample_user_report(self, context: Context, community_id) -> Tuple[dict, MassEnergizeAPIError]:
        data = {'email': context.user_email, "community_id": community_id}
        download_data.delay(data, SAMPLE_USER_REPORT)
        
        return {}, None

    def send_sadmin_report(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, SADMIN_REPORT)
        return [], None
    
    def action_users_download(self, context: Context, action_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'action_id': action_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, ACTION_USERS)
        return [], None

    def policy_download(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in,
            'policy_id': args.get("policy_id"),
            "title": args.get("title"),
        }
        download_data.delay(data, DOWNLOAD_POLICY)
        return [], None
    
    def community_pagemap_download(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, COMMUNITY_PAGEMAP)
        return [], None
    


    def campaign_follows_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'campaign_id': campaign_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, FOLLOWED_REPORT)
        return [], None

    
    def campaign_likes_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'campaign_id': campaign_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in,
        }
        download_data.delay(data, LIKE_REPORT)
        return [], None
    

    def campaign_link_performance_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'campaign_id': campaign_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
        }
        download_data.delay(data, LINK_PERFORMANCE_REPORT)
        return [], None
    
    
    def campaign_performance_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'campaign_id': campaign_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email
        }
        download_data.delay(data, CAMPAIGN_PERFORMANCE_REPORT)
        return [], None


    def campaign_views_performance_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'campaign_id': campaign_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email
        }
        download_data.delay(data, CAMPAIGN_VIEWS_PERFORMANCE_REPORT)
        return [], None
    

    def campaign_interaction_performance_download(self, context: Context, campaign_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'campaign_id': campaign_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email
        }
        download_data.delay(data, CAMPAIGN_INTERACTION_PERFORMANCE_REPORT)
        return [], None