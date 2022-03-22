from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from api.store.download import DownloadStore
from _main_.utils.context import Context
from typing import Tuple
from api.tasks import download_data


class DownloadService:

    def __init__(self):
        self.store = DownloadStore()

    def users_download(self, context: Context, community_id=None, team_id=None) -> Tuple[list, MassEnergizeAPIError]:
        print(type(context))
        data = {
            'community_id': community_id,
            'team_id': team_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email
        }
        download_data.delay(data, 'users')
        return [], None

    def actions_download(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin':context.user_is_super_admin,
            'email': context.user_email
        }
        download_data.delay(data, 'actions')
        return [], None

    def communities_download(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin': context.user_is_super_admin,
            'email': context.user_email
        }
        download_data.delay(data, 'actions')
        return [], None

    def teams_download(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin': context.user_is_super_admin,
            'email': context.user_email
        }
        download_data.delay(data, 'teams')
        return [], None

    def metrics_download(self, context: Context, args, community_id) -> Tuple[list, MassEnergizeAPIError]:
        # communities_download, err = self.store.metrics_download(
        #     context, args, community_id)

        data = {
            'community_id': community_id,
            'user_is_community_admin': context.user_is_community_admin,
            'user_is_super_admin': context.user_is_super_admin,
            'email': context.user_email
        }

        download_data.delay(data, 'metrics')
        return [], None
