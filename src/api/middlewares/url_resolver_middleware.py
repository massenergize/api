from django.http import HttpResponse
from django.urls import resolve, Resolver404
from _main_.hosts import host_patterns
class URLResolverMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Store hosts directly instead of regex patterns
        self.host_patterns = host_patterns

    def __call__(self, request):
        _path = self._resolve_path(request)
        if _path is None:
            return HttpResponse("This endpoint does not exist.", status=404)

        # request.path_info = _path 
        return self.get_response(request)

    def _resolve_path(self, request):
        try:
            current_host = request.get_host().split('.')[0]
            
            # Check if the current host matches any of our patterns
            matching_host = None
            for host in self.host_patterns:
                if str(host.regex).strip('^$') == current_host:
                    matching_host = host
                    break
            
            if matching_host:
                if request.path == '/':
                    _path = f'/{current_host}'
                else:
                    _path = f'/{current_host}{request.path}'
            else:
                _path = request.path

            resolve(_path)  # Check if path is valid
            return _path
        except Resolver404 as e:
            print("===ERROR===", str(e))
            return None
