from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context


class DownloadStore:

  def __init__(self):
    self.name = "Download Store/DB"

  # TODO: implement. for both routes...
  # if community_id given AND user is community admin -> return data for that community
  # if no community id given AND user is super admin -> return all data

  def users_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      return [["Foo", "Bar", "Baz"]], None
    except Exception as e:
      return None, CustomMassenergizeError(e)

  def actions_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      return [["Baz", "Bar", "Foo"]], None
    except Exception as e:
      return None, CustomMassenergizeError(e)
