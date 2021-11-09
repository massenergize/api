from typing import Tuple
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from api.store.media_library import MediaLibraryStore


class MediaLibraryService:
    def __init__(self):
        self.__init__()
        self.store = MediaLibraryStore()

    def back_fill_user_media_uploads(self, args) -> Tuple [list, MassEnergizeAPIError]:
        content = self.store.back_fill_user_media_uploads(self, args)  
        ser = [m.full_json() for m in content]
        return ser, None