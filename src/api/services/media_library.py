from typing import Tuple
from _main_.utils.common import serialize_all
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from api.store.media_library import MediaLibraryStore


class MediaLibraryService:
    def __init__(self):
        self.store = MediaLibraryStore()

    def fetch_content(self, args) -> Tuple[list, MassEnergizeAPIError]:
        images, error = self.store.fetch_content(args)
        if error:
            return None, error
        return serialize_all(images), None
