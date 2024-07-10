from sentry_sdk import capture_message
from _main_.utils.massenergize_errors import CustomMassenergizeError
from database.models import TextHash
from typing import Tuple

class TextHashStore:
    def __init__(self):
        self.name = "Text Hash Store/DB"

    def get_text_hash_info (self, context, args) -> Tuple[ dict, any ]:
        try:
            hash = args.get('hash', None)
            text_hash = None #

            if hash:
                text_hash = TextHash.objects.filter(hash=hash).first()
            else:
                return None, CustomMassenergizeError("Please provide a valid hash")

            if not text_hash:
                return None, CustomMassenergizeError("Text hash not found")

            return text_hash, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(str(e))

    def create_text_hash (self, context, args) -> Tuple[ TextHash, None ]:
        try:
            text_hash, _ = TextHash.objects.get_or_create(hash = args.get('hash', None), text = args.get('text', None))

            return text_hash, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, e

    def list_text_hashes (self, context, args) -> Tuple[ list, any ]:
        try:
            text_hashes = TextHash.objects.all()
            return text_hashes, None
        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(str(e))
