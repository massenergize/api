from django.http import HttpResponse
from django.urls import resolve, Resolver404

class GateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            resolve(request.path)
        except Resolver404:
            return HttpResponse("This endpoint does not exist.", status=404)
        
        response = self.get_response(request)
        return response
     

        