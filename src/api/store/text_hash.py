from _main_.utils.massenergize_errors import CustomMassenergizeError
from database.models import TextHash
from _main_.utils.massenergize_logger import log
from typing import Tuple, Union, Any

NO_HASH_PROVIDED = "No hash provided"
TEXT_HASH_NOT_FOUND = "Text hash not found"
INVALID_HASH_ERR_MSG = "Invalid hash provided"


class TextHashStore:
    """
    DEPRECATED (DO NOT USE):
    This class is deprecated and marked for removal
    """
    def __init__(self):
        self.name = "Text Hash Store/DB"

    def get_text_hash_info (self, args) -> Union[tuple[None, CustomMassenergizeError], tuple[Any, None]]:
        try:
            hash = args.get('hash', None)
            if not hash:
                return None, CustomMassenergizeError(INVALID_HASH_ERR_MSG)

            text_hash = TextHash.objects.filter(hash=hash).first()
            if not text_hash:
                return None, CustomMassenergizeError(TEXT_HASH_NOT_FOUND)

            return text_hash, None
        except Exception as e:
            log.error(str(e))
            return None, CustomMassenergizeError(str(e))

    def text_hash_exists (self, hash) -> Tuple[ bool, any ]:
        try:
            if not hash:
                return False, CustomMassenergizeError(NO_HASH_PROVIDED)

            text_hash = TextHash.objects.filter(hash=hash).first()
            return text_hash is not None, None
        except Exception as e:
            log.error(str(e))
            return False, e

    def create_text_hash (self, args) -> Union[tuple[Any, None], tuple[None, Exception]]:
        try:
            text_hash, _ = TextHash.objects.get_or_create(hash = args.get('hash', None), text = args.get('text', None))

            return text_hash, None
        except Exception as e:
            log.error(str(e))
            return None, e

    def list_text_hashes (self,) -> Union[tuple[Any, None], tuple[None, CustomMassenergizeError]]:
        try:
            text_hashes = TextHash.objects.all()
            return text_hashes, None
        except Exception as e:
            log.error(str(e))
            return None, CustomMassenergizeError(str(e))
