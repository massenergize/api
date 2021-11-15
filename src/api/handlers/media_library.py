from _main_.utils.context import Context
from _main_.utils.route_handler import RouteHandler
from api.services.media_library import MediaLibraryService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import CustomMassenergizeError
from database.models import Service


class MediaLibraryHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = MediaLibraryService()
        self.registerRoutes()

    def registerRoutes(self):
        self.add("/gallery.fetch", self.fetch_content)
        self.add("/gallery.search", self.search)
        self.add("/gallery.remove", self.remove)
        self.add("/gallery.add", self.addToGallery)
        self.add("/gallery.remove", self.remove)
        self.add("/gallery.image.info", self.getImageInfo)
        # self.add("/gallery.backfill", self.back_fill_user_media_uploads)

    def fetch_content(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("community_id", int, is_required=True)
        self.validator.expect("lower_limit", int, is_required=False)
        self.validator.expect("upper_limit", int, is_required=False)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return MassenergizeResponse(error=str(err))
        images, error = self.service.fetch_content(args)
        if error:
            return MassenergizeResponse(error=str(error))
        return MassenergizeResponse(data=images)

    def search(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("community_id", int, is_required=True)
        self.validator.expect("scope", str, is_required=True)
        self.validator.expect("lower_limit", int, is_required=False)
        self.validator.expect("upper_limit", int, is_required=False)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return MassenergizeResponse(error=str(err))

        images, error = self.service.search(args)
        if error:
            return MassenergizeResponse(error=str(error))
        return MassenergizeResponse(data=images)

    def remove(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("media_id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return MassenergizeResponse(error=str(err))

        response, error = self.service.remove(args)
        if error:
            return MassenergizeResponse(error=str(error))
        return MassenergizeResponse(data=response)

    def addToGallery(self, request):
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("user_id", str, is_required=True).expect(
            "community_id", int, is_required=True
        ).expect("title", str, is_required=False).expect(
            "file", "file", is_required=True
        )
        args, err = self.validator.verify(args, strict=True)
        if err:
            return MassenergizeResponse(error=str(err))
        image, error = self.service.addToGallery(args)
        if error:
            return MassenergizeResponse(error=str(error))
        return MassenergizeResponse(data=image)

    def getImageInfo(self):
        pass
