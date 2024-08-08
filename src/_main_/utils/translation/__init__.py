import re
from typing import Union, Tuple, List
from _main_.utils.massenergize_logger import log
from _main_.utils.translation.translator import Translator, MAX_TEXT_SIZE, MAGIC_TEXT
from _main_.utils.utils import make_hash, run_in_background
from database.models import TranslationsCache
import json_flatten

JSON_EXCLUDE_KEYS = {
    'id', 'pk', 'file', 'media', 'date', 'link', 'url', 'icon', 'key', 'slug'
}

JSON_EXCLUDE_VALUES = {
    "null",
    "undefined",
    "None",
    "True",
    "False",
    "null",
    "false",
    "true",
    "",
    # let's add some common JSON string values that should not be translated
}

EXCLUDED_JSON_VALUE_PATTERNS = [
    re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),                   #  EMAIL_REGEX
    re.compile("(https?://)?\w+(\.\w+)+"),                                          #  URL_REGEX
    re.compile("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),     #  UUID_REGEX
    re.compile(r'\b(\d{4})-(0?[1-9]|1[0-2])-(0?[1-9]|[12]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d)\.(\d{3})Z\b'),                     #  DATE_REGEX
    re.compile("\d{4}-\d{2}-\d{2}"),                                                #  SHORT_DATE_REGEX
    re.compile(r'\b\d+\b')
]


class JsonTranslator(Translator):
    def __init__ (self, dict_to_translate: Union[dict, list], exclude_keys = None, exclude_cached = False):
        super().__init__()
        self.exclude_keys = set(exclude_keys) if exclude_keys else set()
        self.sep = '.'
        self.dict_to_translate = dict_to_translate
        self._exclude_cached = exclude_cached
        self.translations_cache = TranslationsCache()
        self.cached_translations = None
        self._flattened, self._excluded = self.flatten_json_for_translation(self.dict_to_translate)
    
    def flatten_json_for_translation(self, json_to_translate: Union[dict, list]):
        assert (json_to_translate is not None) and (
            isinstance(json_to_translate, dict) or isinstance(json_to_translate, list))
        
        flattened_dict_for_keys_to_include = {}
        flattened_dict_for_keys_to_exclude = {}
        
        flattened = json_flatten.flatten(json_to_translate)
        
        for k, v in flattened.items():
            real_key = k.split(".")[-1].split("$")[0]
            if self._should_exclude(real_key, v):
                flattened_dict_for_keys_to_exclude[k] = v
            else:
                flattened_dict_for_keys_to_include[k] = v
        
        return flattened_dict_for_keys_to_include, flattened_dict_for_keys_to_exclude

    def _is_excluded_pattern(self, value: str):
        return any(pattern.fullmatch(value) for pattern in EXCLUDED_JSON_VALUE_PATTERNS)

    def _should_exclude(self, key, _value):
        # add more checks here

        # Check if key is in exclude_keys or JSON_EXCLUDE_KEYS
        if key in self.exclude_keys or key in JSON_EXCLUDE_KEYS:
            return True

        # Check if value is not a string.  For eg. we want to exclude types like bool, int etc
        if not isinstance(_value, str):
            return True

        # Check if value is in JSON_EXCLUDE_VALUES
        if _value in JSON_EXCLUDE_VALUES or self._is_excluded_pattern(_value):
            return True

        # Default: include the key-value pair
        return False
    
    def unflatten_dict(self, flattened: dict):
        all_flattened = flattened

        # now add the keys that got removed during initialization because of the exclusion set
        all_flattened.update(self._excluded)

        assert all_flattened is not None
        return json_flatten.unflatten(all_flattened)

    def _parse_key(self, key: str):
        parts = key.split(self.sep)
        keys = []
        for part in parts:
            if part.startswith('[') and part.endswith(']'):
                keys.append(int(part[1:-1]))
            else:
                keys.append(part)
        return keys

    def _ensure_list_size (self, lst, size, padding = None):
        if len(lst) < size:
            lst.extend([padding] * (size - len(lst)))
        return lst

    def get_flattened_dict(self):
        return self._flattened

    def get_flattened_dict_for_excluded_keys(self):
        return self._excluded
        
    @run_in_background
    def cache_translations(sef, raw_texts, translated_text_list, target_language, source_language):
        try:
            for text, translated_text in zip(raw_texts, translated_text_list):
                _hash = make_hash(text)
                existing_translations = TranslationsCache.objects.filter(
                    hash=_hash,
                    target_language_code=target_language,
                    source_language_code=source_language
                )
                if not existing_translations.exists():
                    TranslationsCache.objects.create(
                        hash=_hash,
                        target_language_code=target_language,
                        source_language_code=source_language,
                        translated_text=translated_text
                    )
                else:
                    for translation in existing_translations:
                        translation.translated_text = translated_text
                        translation.save()
            
            return True
        except Exception as e:
            log.exception(e)
            return False
    
    def separate_translated_and_untranslated(self, target_language: str, source_language: str):
        flattened_translated_dict = {}
        flattened_untranslated_dict = {}
        
        flattened_values = list(self._flattened.values())
        hashes = set(make_hash(value) for value in flattened_values)
        
        translations = TranslationsCache.objects.filter(target_language_code=target_language, hash__in=hashes, source_language_code=source_language)
        
        for key, value in self._flattened.items():
            hash_key = make_hash(value)
            translation = translations.filter(hash=hash_key).first()
            if translation:
                flattened_translated_dict[key] = translation.translated_text
            else:
                flattened_untranslated_dict[key] = value
        
        return flattened_translated_dict, flattened_untranslated_dict
    
    def translate(self, source_language: str, destination_language: str) -> Tuple[dict, List[str], List[dict]]:
        """
        Translate the flattened dictionary values from source_language to destination_language.

        Returns:
            tuple: The translated dictionary in its original nested structure.
        """
        
        translated_flattened, untranslated_flattened = self.separate_translated_and_untranslated(destination_language, source_language)
        untranslated_text_entries = list(untranslated_flattened.values())
        keys = list(untranslated_flattened.keys())

        # TODO: We should parallelize this
        #  We can plit the list into chunks of maybe 10 and
        #  have the job of the translation done in several threads and the results combined.

        # convert values to text batches
        text_batches = self.convert_to_text_batches(untranslated_text_entries, max_batch_size = self.MAX_TEXT_SIZE)
        # Translate text batches
        translated_batches = self._translate_text_batches(text_batches,source_language,destination_language)
        # Flatten translated batches back to individual translations
        translated_text_entries = self.flatten_text_batches(translated_batches)

        # Ensure the translation count matches the original count
        assert len(untranslated_text_entries) == len(translated_text_entries), "Mismatch between original and translated text entries"

        # Reconstruct the translated JSON
        translated_json = {keys[i]: translated_text_entries[i] for i in range(len(keys))}
        translated_json.update(translated_flattened)
        translated_json.update(self._excluded)
        
        if len(untranslated_text_entries) > 0:
            self.cache_translations(untranslated_text_entries, translated_text_entries, destination_language, source_language)

        return self.unflatten_dict(translated_json), translated_text_entries, untranslated_text_entries

    def convert_to_text_blocks(self, text_list, max_block_size=MAX_TEXT_SIZE, magic_text=MAGIC_TEXT):
        """
        Convert a list of text entries into blocks that do not exceed the MAX_TEXT_SIZE limit.
        We use MAGIC_TEXT to separate text items or sentences within a block during translation, allowing us to split them back afterward.
        Translation APIs, like Google Translate, have a maximum text length they can handle. The idea of a block here
        represents a text blob that does not exceed that maximum length.
        If we have many text elements or sentences to translate, we combine them into blocks, ensuring each block
        does not exceed the maximum length. Each block contains several of these sentences separated by MAGIC_TEXT.

        Args:
            text_list (list): List of text entries to be translated.

        Returns:
            list: List of text blocks.
        """
        blocks = []
        current_block = ""

        for text in text_list:
            if len(current_block) + len(magic_text) + len(text) > max_block_size:
                blocks.append(current_block)
                current_block = text
            else:
                if current_block:
                    current_block += (magic_text + text)
                else:
                    current_block = text

        if current_block:
            blocks.append(current_block)

        return blocks

    def _translate_text_blocks(self, text_blocks, source_language, destination_language):
        """
        Translate a list of text blocks from source_language to destination_language.

        Args:
            text_blocks (list): List of text blocks to be translated.
            source_language (str): Source language code.
            destination_language (str): Destination language code.

        Returns:
            list: List of translated text blocks.
        """
        translated_blocks = []
        for block in text_blocks:
            translated = self.translate_text(block, source_language, destination_language)
            translated_blocks.append(translated)

        return translated_blocks

    def _unwind_translated_blocks(self, translated_blocks):
        """
        Split translated text blocks back into individual translations.

        Args:
            translated_blocks (list): List of translated text blocks.

        Returns:
            list: List of individual translated text entries.
        """
        translations = []
        for block in translated_blocks:
            translations.extend(block.split(MAGIC_TEXT))

        return translations

    def convert_to_text_batches(self, text_list, max_batch_size=MAX_TEXT_SIZE) -> List[List[str]]:
        """
        Convert a list of text entries into batches that do not exceed the MAX_TEXT_SIZE limit.
        Translation APIs, like Google Translate, have a maximum text length they can handle. The idea of a batch here
        represents a text blob that does not exceed that maximum length.
        If we have many text elements or sentences to translate, we combine them into batches, ensuring each batch
        does not exceed the maximum length.

        Args:
            text_list (list): List of text entries to be translated.

        Returns:
            list: List of text batches.
        """
        batches = []
        current_batch = []
        length_of_current_batch = 0
        MAX_BATCH_LENGTH = 128


        for text in text_list:
            if length_of_current_batch + len(text) > max_batch_size:
                batches.append(current_batch)
                current_batch = [text]
                length_of_current_batch = len(text)
            else:
                length_of_current_batch += len(text)

                if len(current_batch) < MAX_BATCH_LENGTH:
                    current_batch.append(text)
                else:
                    batches.append(current_batch)
                    current_batch = [text]
                    length_of_current_batch = len(text)

        if current_batch:
            batches.append(current_batch)

        return batches

    def _translate_text_batches(self, text_batches : List[List[str]], source_language, destination_language):
        """
        Translate a list of text batches from source_language to destination_language.

        Args:
            text_batches (list): List of text batches to be translated.
            source_language (str): Source language code.
            destination_language (str): Destination language code.

        Returns:
            list: List of translated text batches.
        """
        translated_batches = []
        for batch in text_batches:
            translated = self.translate_batch(batch, source_language, destination_language)
            translated_batches.append(translated)

        return translated_batches

    def flatten_text_batches(self, text_batches : List[List[str]]):
        """
        Flatten a list of text batches into a single list of text entries.

        Args:
            text_batches (list): List of text batches.

        Returns:
            list: List of text entries.
        """
        text_list = []
        for batch in text_batches:
            text_list.extend(batch)

        return text_list
