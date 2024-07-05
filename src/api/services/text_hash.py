import hashlib

from _main_.utils.massenergize_errors import CustomMassenergizeError
from api.store.text_hash import TextHashStore


class TextHashService:
    def __init__(self, text: str):
        self.store = TextHashStore()

    def make_hash(self):
        return hashlib.sha256(self.text.encode()).hexdigest()

    def create_text_hash(self, context, args):
        hash = self.make_hash()
        args['hash'] = hash
        return self.store.create_text_hash(context, args)

    def get_text_hash_info(self, context, args):
        text_hash = self.store.get_text_hash_info(context, args)

        if text_hash:
            return text_hash, None
        return None, CustomMassenergizeError("Could not get text hash info")

    def list_text_hashes(self, context, args):
        text_hashes = self.store.list_text_hashes(context, args)

        if text_hashes:
            return text_hashes, None

        return [], CustomMassenergizeError("Could not list text hashes")
