import hashlib

from _main_.utils.massenergize_errors import CustomMassenergizeError
from api.store.text_hash import TextHashStore


class TextHashService:
    def __init__ (self):
        self.store = TextHashStore()

    @staticmethod
    def make_hash (text: str):
        return hashlib.sha256(text.encode()).hexdigest()

    def create_text_hash (self, args):
        text = args.get('text', None)

        if not text and not isinstance(text, str):
            return None, CustomMassenergizeError("Please provide a valid text")

        hash = TextHashService.make_hash(text)
        args[ 'hash' ] = hash

        text_hash, err = self.store.create_text_hash(args)

        if err:
            print("CTxH ERR", err)
            return None, err

        return text_hash, None

    def get_text_hash_info (self, context, args):
        text_hash, err = self.store.get_text_hash_info(args)

        if err:
            return None, err
        return text_hash, None

    def list_text_hashes (self, context, args):
        text_hashes, err = self.store.list_text_hashes(context, args)

        if err:
            return None, err

        return text_hashes, None
