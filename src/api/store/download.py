from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context


class DownloadStore:

  def __init__(self):
    self.name = "Download Store/DB"

  # TODO: implement store methods