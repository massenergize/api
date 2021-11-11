from typing import Tuple
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from carbon_calculator.models import Action
from database.models import Media
from django.db.models import Q

limit = 30


class MediaLibraryStore:
    def __init__(self):
        self.name = "MediaLibrary Store/DB"

    def fetch_content(self, args):
        com_id = args["community_id"]
        upper_limit = lower_limit = images = None
        try:
            upper_limit = args["upper_limit"]
            lower_limit = args["lower_limit"]
        except KeyError:
            pass
        if not upper_limit and not lower_limit:
            images = Media.objects.filter(
                Q(events__community__id=com_id)
                | Q(actions__community__id=com_id)
                | Q(testimonials__community__id=com_id)
            ).order_by("-id")[:limit]
        else:
            images = Media.objects.filter(
                Q(events__community__id=3)
                | Q(actions__community__id=3)
                | Q(testimonials__community__id=3),
                id__gt=upper_limit,
                id__lt=lower_limit,
            ).order_by("-id")[:limit]
        return images, None
