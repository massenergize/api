from _main_.utils.common import serialize_all
from api.store.media_library import MediaLibraryStore
from database.utils.common import get_json_if_not_none


class MediaLibraryService:
    def __init__(self):
        self.store = MediaLibraryStore()

    def read_image(self, args):
        string, error = self.store.read_image(args)
        if error:
            return None, error
        return string, None

    def print_duplicates(self, args, context):
        response, error = self.store.print_duplicates(args, context)
        if error:
            return None, error
        # return serialize_all(response), None
        return response, None
    
    def clean_duplicates(self, args, context):
        response, error = self.store.clean_duplicates(args, context)
        if error:
            return None, error
        # return serialize_all(response), None
        return response, None
    
    def summarize_duplicates(self, args, context):
        response, error = self.store.summarize_duplicates(args, context)
        if error:
            return None, error
        # return serialize_all(response), None
        return response, None
    
    def generate_hashes(self, args, context):
        response, error = self.store.generate_hashes(args, context)
        if error:
            return None, error
        return response, None
    
    def fetch_content(self, context, args):
        images, error = self.store.fetch_content(context, args)
        if error:
            return None, error
        return self.organiseData(data=serialize_all(images, True), args=args), None

    def search(self, args, context):
        images, meta, error = self.store.search(args, context)
        if error:
            return None, error
        organised = self.organiseData(data=serialize_all(images), args=args)
        organised["meta"] = meta
        return organised, None

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

    def remove(self, args, context):
        response, error = self.store.remove(args, context)
        if error:
            return None, error
        return response, None

    def addToGallery(self, args, context):
        image, error = self.store.addToGallery(args, context)
        if error:
            return None, error
        return image.simple_json(), None

    def edit_details(self, args, context):
        media, error = self.store.edit_details(args, context)
        if error:
            return None, error
        if media:
            return self.getImageInfo(
                {"media_id": media.id}
            )  # Refer back to the getinfo routine so that data can be returned in the same structture
        return {}, None

    def find_images(self, args, context):
        images, error = self.store.find_images(args, context)
        if error:
            return None, error
        images = serialize_all(images)
        return images, None

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
        vendors = serialize_all(media.vender_logo.all())  # yhup, thats right. lmfao!
        media_json = get_json_if_not_none(media, True)
        return {
            **media_json,
            "information": user_info,
            "relations": {
                "event": events,
                "action": actions,
                "testimonial": testimonials,
                "vendor": vendors,
            },
        }, None
