from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import re
import fnmatch

credentials = service_account.Credentials.from_service_account_file(
  filename='./translation-poc-419409-a245f8fb9662.json')
# filename='../../translation-poc-419409-a245f8fb9662.json')
scopes = ['https://www.googleapis.com/auth/cloud-platform']
google_translate_client = translate.Client(credentials=credentials)

PROVIDER = "google"

class TranslationService:
  def __init__(self):
    pass

  def translate (self, values, target_language, source_language='en'):
    if PROVIDER == "google":
      return google_translate_client.translate(values, target_language=target_language, source_language=source_language)
    raise Exception("Invalid translation provider")

  def translate_text(self, text, target_language):
    try:
      result = self.translate(text, target_language=target_language)
      return result['translatedText']
    except Exception as e:
      print(f"Failed to translate text: {e}")
      raise e

  def translate_batch (self, texts:list, target_language, source_language='en'):
    try:
      return self.translate(texts, target_language=target_language, source_language=source_language)
    except Exception as e:
      print(f"Failed to translate text: {e}")
      raise e

  def translate_json(self, json_dict: dict, target_language: str, ignore_keys=None, ignore_patterns=None, batch_size=128):
    translation_queue = []
    key_mapping = {}

    def is_translatable(text, key):
      EMAIL_REGEX = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
      URL_REGEX = "(https?://)?\w+(\.\w+)+"
      UUID_REGEX = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
      DATE_REGEX = "'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z"
      SHORT_DATE_REGEX = "\d{4}-\d{2}-\d{2}"
      DEFAULT_IGNORE_LIST = [
        "null",
        "undefined",
        "None",
        "True",
        "False",
        "null",
        "false",
        "true",
        # let's add some common JSON keyword that should not be translated
      ]

      if ignore_keys and any(fnmatch.fnmatch(key, pattern) for pattern in ignore_keys):
        return False
      elif ignore_patterns and any(re.fullmatch(pattern, text) for pattern in ignore_patterns):
        return False

      return not (re.fullmatch(EMAIL_REGEX, text) or
                  re.fullmatch(URL_REGEX, text) or
                  re.fullmatch(UUID_REGEX, text) or
                  re.fullmatch(DATE_REGEX, text) or
                  re.fullmatch(SHORT_DATE_REGEX, text) or
                  text in DEFAULT_IGNORE_LIST or
                  text.isspace())

    def collect_translatable(json_struct: dict, current_key=""):
      if isinstance(json_struct, dict):
        for key in json_struct:
          new_key = current_key + "." + key if current_key else key
          json_struct[key] = collect_translatable(json_struct[key], new_key)

      elif isinstance(json_struct, list):
        for idx, item in enumerate(json_struct):
          new_key = current_key + "." + str(idx)
          json_struct[idx] = collect_translatable(item, new_key)

      elif isinstance(json_struct, str) and is_translatable(json_struct, current_key):
        translation_queue.append(json_struct)
        if json_struct not in key_mapping:
          key_mapping[json_struct] = []
        key_mapping[json_struct].append(current_key)

      return json_struct

    collect_translatable(json_dict)

    for i in range(0, len(translation_queue), batch_size):
      translations = self.translate(translation_queue[i:i + batch_size], target_language=target_language)

      for translation in translations:
        translated_text = translation['translatedText']
        original_text = translation['input']

        for key_path in key_mapping[original_text]:
          keys = key_path.split('.')
          item_to_replace = json_dict

          for key in keys[:-1]:
            if key.isdigit():
              item_to_replace = item_to_replace[int(key)]
            else:
              item_to_replace = item_to_replace[key]
          if keys[-1].isdigit():
            item_to_replace[int(keys[-1])] = translated_text
          else:
            item_to_replace[keys[-1]] = translated_text

    return json_dict
