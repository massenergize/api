from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from api.store.download import DownloadStore
from _main_.utils.context import Context
from typing import Tuple

class DownloadService:

    def __init__(self):
      self.store = DownloadStore()

    def users_download(self, context: Context, community_id=None, team_id=None) -> Tuple[list, MassEnergizeAPIError]:
      users_download, err = self.store.users_download(context, community_id, team_id)
      return users_download, err

    def actions_download(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
      actions_download, err = self.store.actions_download(context, community_id)
      return actions_download, err

    def communities_download(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
      communities_download, err = self.store.communities_download(context)
      return communities_download, err

    def teams_download(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
      teams_download, err = self.store.teams_download(context, community_id)
      return teams_download, err
    
    def metrics_download(self, context: Context, args, community_id) -> Tuple[list, MassEnergizeAPIError]:
      communities_download, err = self.store.metrics_download(context, args, community_id)
      return communities_download, err
