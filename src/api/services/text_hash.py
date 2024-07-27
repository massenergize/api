import hashlib
import logging

from _main_.utils.massenergize_errors import CustomMassenergizeError
from api.store.text_hash import TextHashStore


class TextHashService:
    """
    DEPRECATED (DO NOT USE):
    This class is deprecated and marked for removal
    """
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
            logging.error("Error creating text hash: %s", err)
            return None, err

        return text_hash, None

    def get_text_hash_info (self, context, args):
        text_hash, err = self.store.get_text_hash_info(args)

        if err:
            return None, err
        return text_hash, None

    def text_hash_exists (self, text):
        """
        Check if a text hash exists in the database

        :param context: The request context
        :param args: a dictionary containing the text to be hashed
            :key text: The text to be hashed

        :return: A tuple containing a boolean indicating if the text hash exists and an error message
        """
        exists, err = self.store.text_hash_exists(hash=TextHashService.make_hash(text))

        if err:
            return False, err

        return exists, None
