from typing import Tuple
from _main_.utils.massenergize_errors import MassEnergizeAPIError


class MediaLibraryStore:
    def __init__(self):
        self.name = "MediaLibrary Store/DB"

    def back_fill_user_media_uploads(self, args) -> Tuple[dict, MassEnergizeAPIError]:
        """
				* Go through actions, doe
				
				
				"""
        
