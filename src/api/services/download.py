from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.download import DownloadStore
from _main_.utils.context import Context

class DownloadService:

    def __init__(self):
      self.store = DownloadStore()

    def users_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
      users_download, err = self.store.users_download(context, community_id)
      if err:
        return None, err
      return users_download, None

    def actions_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
      actions_download, err = self.store.actions_download(context, community_id)
      if err:
        return None, err
      return actions_download, None

    def communities_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
      communities_download, err = self.store.communities_download(context, community_id)
      if err:
        return None, err
      return communities_download, None

    def teams_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
      teams_download, err = self.store.teams_download(context, community_id)
      if err:
        return None, err
      return teams_download, None
