from typing import Tuple
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from carbon_calculator.models import Action
from database.models import Media
from django.db.models import Q


class MediaLibraryStore:
    def __init__(self):
        self.name = "MediaLibrary Store/DB"
    
    def back_fill_user_media_uploads(self, args) -> Tuple[list, MassEnergizeAPIError]: 
        content = Media.objects.filter(Q(events__community__id=3) | Q(actions__community__id =3))
        if not content:
            return [], None 
        return content, None

