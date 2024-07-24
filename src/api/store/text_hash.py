from _main_.utils.massenergize_errors import CustomMassenergizeError
from database.models import TextHash
from _main_.utils.massenergize_logger import log
from typing import Tuple

class TextHashStore:
    def __init__(self):
        self.name = "Text Hash Store/DB"

    def get_text_hash_info (self, args) -> Tuple[ dict, any ]:
        try:
            hash = args.get('hash', None)
            if not hash:
                return None, CustomMassenergizeError("Invalid hash provided")

            text_hash = TextHash.objects.filter(hash=hash).first()
            if not text_hash:
                return None, CustomMassenergizeError("Text hash not found")

            return text_hash, None
        except Exception as e:
            log.error(str(e))
            return None, CustomMassenergizeError(str(e))

    def text_hash_exists (self, hash) -> Tuple[ bool, any ]:
        try:
            if not hash:
                return False, CustomMassenergizeError("No hash provided")

            text_hash = TextHash.objects.filter(hash=hash).first()
            return text_hash is not None, None
        except Exception as e:
            log.error(str(e))
            return False, e

    def create_text_hash (self, args) -> Tuple[ TextHash, None ]:
        try:
            text_hash, _ = TextHash.objects.get_or_create(hash = args.get('hash', None), text = args.get('text', None))

            return text_hash, None
        except Exception as e:
            log.error(str(e))
            return None, e

    def list_text_hashes (self,) -> Tuple[ list, any ]:
        try:
            text_hashes = TextHash.objects.all()
            return text_hashes, None
        except Exception as e:
            log.error(str(e))
            return None, CustomMassenergizeError(str(e))
