from django.test import SimpleTestCase, RequestFactory
from django.http import HttpResponse
from api.middlewares.url_resolver_middleware import URLResolverMiddleware

class URLResolverMiddlewareTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = URLResolverMiddleware(get_response=self.get_response)

    def get_response(self, request):
        return HttpResponse("Middleware passed")

    def test_resolve_existing_host(self):
        request = self.factory.get('/', HTTP_HOST='localhost')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.path_info, '/')

    def test_resolve_existing_host_with_path(self):
        request = self.factory.get('/api/auth.logout', HTTP_HOST='localhost')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.path_info, '/api/auth.logout')

    def test_resolve_existing_host_with_path_2(self):
        request = self.factory.get('/auth.logout', HTTP_HOST='api.test.com')
        url = URLResolverMiddleware._resolve_path(self.middleware, request)
        self.assertEqual(url, '/api/auth.logout')

    def test_resolve_non_existing_host(self):
        request = self.factory.get('/', HTTP_HOST='mc.test.com')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.path_info, '/')

    def test_resolve_non_existing_path(self):
        request = self.factory.get('/nonexistent/path', HTTP_HOST='localhost')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), "This endpoint does not exist.")

