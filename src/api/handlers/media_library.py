from _main_.utils.context import Context
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only
from api.services.media_library import MediaLibraryService
from _main_.utils.massenergize_response import MassenergizeResponse


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
        self.add("/gallery.find", self.findImages)

    @admins_only
    def fetch_content(self, request):
        """Fetches image content related communities that admins can browse through"""
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("community_ids", "str_list", is_required=True)
        self.validator.expect("lower_limit", int, is_required=False)
        self.validator.expect("upper_limit", int, is_required=False)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err
        images, error = self.service.fetch_content(args)
        if error:
            return error
        return MassenergizeResponse(data=images)

    @admins_only
    def search(self, request):
        """Filters images and only retrieves content related to a scope(events, testimonials,actions etc). More search types to be added later when requested..."""
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("lower_limit", int).expect("upper_limit", int).expect(
            "all_communities", bool
        ).expect("filters", "str_list", is_required=True).expect(
            "target_communities", list, is_required=True
        ).expect(
            "any_community", bool
        ).expect(
            "tags", "str_list"
        )
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        args["context"] = context
        images, error = self.service.search(args)
        if error:
            return error
        return MassenergizeResponse(data=images)

    @admins_only
    def remove(self, request):
        """Deletes a media file from the system"""
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("media_id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        response, error = self.service.remove(args,context)
        if error:
            return error
        return MassenergizeResponse(data=response)

    def addToGallery(self, request):
        """Enables admins to upload images that they can use later..."""
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("user_id", str, is_required=True).expect(
            "community_ids", list
        ).expect("title", str).expect("file", "file", is_required=True).expect(
            "is_universal", bool
        ).expect(
            "tags", "str_list"
        ).expect("size",str).expect("size_text", str).expect("description").expect("underAge", bool).expect("copyright", bool).expect("copyright_att", str).expect("guardian_info", str)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err
        image, error = self.service.addToGallery(args,context)
        if error:
            return error
        return MassenergizeResponse(data=image)

    @admins_only
    def getImageInfo(self, request):
        """Retrieves information about an image file when given media_id"""
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("media_id", int, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        response, error = self.service.getImageInfo(args)
        if error:
            return error
        return MassenergizeResponse(data=response)
    
    def findImages(self, request):
        """Retrieves images given a list of media_ids"""
        context: Context = request.context
        args: dict = context.args
        self.validator.expect("ids", list, is_required=True)
        args, err = self.validator.verify(args, strict=True)
        if err:
            return err

        response, error = self.service.findImages(args, context)
        if error:
            return error
        return MassenergizeResponse(data=response)
