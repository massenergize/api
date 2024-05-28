from _main_.utils.route_handler import RouteHandler
from api.services.download import DownloadService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only
from api.services.translation import TranslationService
from api.utils.translate_json import translate_json


class TranslationHandler(RouteHandler):
  def __init__(self):
    super().__init__()
    self.service = TranslationService()
    self.register_routes()


  def register_routes(self) -> None:
    self.add("/translations.get", self.get)

  def get(self, request) -> MassenergizeResponse:
    context: Context = request.context
    args = context.get_request_body()
    text = args.get('text', '')
    target_language = args.get('target_language', 'en')

    print("text", text, "target_language", target_language)

    # translations, err = self.service.translate_text(text = text, target_language = target_language)
    translation = translate_json({
        "person": {
          "name": "John Doe", "age": 30
        },
        "description": "This is a description",
        "url": "https://www.example.com",
        "email": "abc@efg.xyz",
        "nested": {
          "url": "https://www.example.com",
          "email": "abc@efg.xyz",
        },
        "list": ["https://www.example.com", "abc@efg.xyz", "This is a description in a list"],
        "transalatble": "This is a translatable text",
      }, target_language=target_language)

    print("translations", translation)

    # if err:
    #   return err
    return MassenergizeResponse(data=translation)
