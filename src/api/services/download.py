from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.event import DownloadStore
from _main_.utils.context import Context

class DownloadService:

    def __init__(self):
      self.store = DownloadStore()

    # TODO: implement services