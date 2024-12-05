from django.http import HttpResponse
from django.urls import resolve, Resolver404
from _main_.hosts import host_patterns


class URLResolverMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.host_map = {host.regex: host for host in host_patterns}

    def __call__(self, request):
        resolved_path = self._resolve_path(request)
        if resolved_path is None:
            return HttpResponse("This endpoint does not exist.", status=404)

        request.path_info = resolved_path 
        return self.get_response(request)

    def _resolve_path(self, request):
        try:
            current_host = request.get_host().split('.')[0]
            if current_host in self.host_map:
               if request.path == '/':
                    resolved_path = f'/{current_host}'
               else:
                    resolved_path = f'/{current_host}{request.path}'
            else:
                resolved_path = request.path

            resolve(resolved_path)
            return resolved_path
        except Resolver404:
            return None
