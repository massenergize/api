from django.http import HttpResponse
from django.urls import resolve, Resolver404
from _main_.hosts import host_patterns
class URLResolverMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.host_map = {host.regex: host for host in host_patterns}

    def __call__(self, request):
        _path = self._resolve_path(request)
        if _path is None:
            return HttpResponse("This endpoint does not exist.", status=404)

        # request.path_info = _path 
        return self.get_response(request)

    def _resolve_path(self, request):
        try:
            current_host = request.get_host().split('.')[0]
            if current_host in self.host_map:
               if request.path == '/':
                    _path = f'/{current_host}'
               else:
                    _path = f'/{current_host}{request.path}'
            else:
                _path = request.path

            resolve(_path)  # Check if path is valid
            return _path
        except Resolver404:
            return None
