from typing import Tuple
from _main_.utils.common import serialize_all
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.utils import Console
from api.store.media_library import MediaLibraryStore
from carbon_calculator.models import Event
from database.utils.common import get_json_if_not_none


class MediaLibraryService:
    def __init__(self):
        self.store = MediaLibraryStore()

    def fetch_content(self, args):
        images, error = self.store.fetch_content(args)
        if error:
            return None, error
        data = serialize_all(images)
        first = data[0]
        last = data[len(data) - 1]
        return {
            "upper_limit": first.get("id"),
            "lower_limit": last.get("id"),
            "data": data,
        }, None

    def search(self, args):
        images, error = self.store.search(args)
        if error:
            return None, error
        return serialize_all(images), None 
        # return images, None

    def remove(self, args):
        response, error = self.store.remove(args)
        if error:
            return None, error
        return response, None

    def addToGallery(self, args):
        image, error = self.store.addToGallery(args)
        if error:
            return None, error
        return image.simple_json(), None

    def getImageInfo(self, args):
        media, error = self.store.getImageInfo(args)
        user_info = events = actions = testimonials = media_json = None
        if error:
            return None, error
        try:
            user_info = get_json_if_not_none(media.user_upload)
        except:
            pass
        events = serialize_all(media.events.all())
        actions = serialize_all(media.actions.all())
        testimonials = serialize_all(media.testimonials.all())
        media_json = get_json_if_not_none(media)
        return {
            **media_json,
            "user_info": user_info,
            "events": events,
            "actions": actions,
            "testimonials": testimonials,
        }, None
