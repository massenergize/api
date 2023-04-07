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
        return self.organiseData(data=serialize_all(images, True), args=args), None

    def search(self, args):
        images, error = self.store.search(args)
        if error:
            return None, error
        return self.organiseData(data=serialize_all(images,True), args=args), None

    def organiseData(self, **kwargs):
        data = kwargs.get("data") or []
        args = kwargs.get("args")
        field = kwargs.get("field")
        if not data or len(data) == 0:
            return {
                "images": [],
                "upper_limit": args.get("upper_limit") or 0,
                "lower_limit": args.get("lower_limit") or 0,
                "description": "No images were found, so limits stay the same...",
            }

        first = data[0]
        last = data[len(data) - 1]
        return {
            "count": len(data),
            "upper_limit": first.get(field or "id"),
            "lower_limit": last.get(field or "id"),
            "images": data,
        }

    def remove(self, args,context):
        response, error = self.store.remove(args,context)
        if error:
            return None, error
        return response, None

    def addToGallery(self, args,context):
        image, error = self.store.addToGallery(args,context)
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
        media_json = get_json_if_not_none(media, True)
        return {
            **media_json,
            "information": user_info,
            "relations": {
                "event": events,
                "action": actions,
                "testimonial": testimonials,
            },
        }, None
