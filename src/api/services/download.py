from _main_.utils.massenergize_errors import MassEnergizeAPIError
from api.constants import ACTIONS, COMMUNITIES, METRICS, TEAMS, USERS, CADMIN_REPORT, SADMIN_REPORT
from api.store.download import DownloadStore
from _main_.utils.context import Context
from typing import Tuple
from api.tasks import download_data


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

    def metrics_download(self, context: Context, args, community_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin': context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
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
        download_data.delay(data, CADMIN_REPORT)  #For testing: download_data(data, CADMIN_REPORT)
        return [], None

    def send_sadmin_report(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email,
            'user_is_logged_in': context.user_is_logged_in
        }
        download_data.delay(data, SADMIN_REPORT)
        return [], None

