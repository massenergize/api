from google.cloud import translate_v2 as translate
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './src/helpers/translation-poc-419409-a245f8fb9662.json'

translate_client = translate.Client()

class TranslationService:
  def __init__(self):
    pass

  def translate_text(self, text, target_language):
    try:
      result = translate_client.translate(text, target_language=target_language)

      return result['translatedText']
    except Exception as e:
      print(f"Failed to translate text: {e}")
      raise e
