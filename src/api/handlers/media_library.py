from _main_.utils.context import Context
from _main_.utils.route_handler import RouteHandler
from api.services.media_library import MediaLibraryService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import CustomMassenergizeError

class MediaLibraryHandler(RouteHandler):
    def __init__(self):
        super().__init__()
        self.service = MediaLibraryService()
        self.registerRoutes()

    def registerRoutes(self):
        self.add("/gallery.fetch", self.fetch_content)
        self.add("/gallery.search", self.search)
        self.add("/gallery.remove", self.remove)
        self.add("/gallery.backfill", self.back_fill_user_media_uploads)

    def fetch_content(self):
        pass

    def search(self):
        pass

    def remove(self):
        pass
    

    
    def back_fill_user_media_uploads(self, request):
        """ Goes over actions, testimonials, events, and teams and collects information about
         uploaders and the community they belong to, to create new instances of UserMediaUploads
         
         """
        context: Context = request.context
        response, error = self.service.back_fill_user_media_uploads(request)
        print(f"This is the count ------------------ {len(response)}----------------")
        return MassenergizeResponse(data = response)