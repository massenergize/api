from _main_.utils.route_handler import RouteHandler
from api.services.download import DownloadService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only
from api.services.translation import TranslationService


class TranslationHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = TranslationService()
    self.registerRoutes()


  def registerRoutes(self) -> None:
    self.add("/translations.get", self.get)

  def get(self, request) -> MassenergizeResponse:
    context: Context = request.context
    args = context.get_request_body()
    translations, err = self.service.translate_text(context, args)
    if err:
      return err
    return MassenergizeResponse(data=translations)
