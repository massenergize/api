from typing import Tuple
from _main_.utils.common import serialize_all
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from api.store.media_library import MediaLibraryStore


class MediaLibraryService:
    def __init__(self):
        self.store = MediaLibraryStore()

    def back_fill_user_media_uploads(self, args) -> Tuple[list, MassEnergizeAPIError]:
        content = self.store.back_fill_user_media_uploads(args)
        combined = []
        count = 0
        for img in content:
            count = count + 1
            # print(f"-----Number - {count}-------")
            if img:
                for k in img:
                    combined.append(k.simple_json())
        return combined, None