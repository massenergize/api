from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns(
  '',
  host(r'search', settings.ROOT_URLCONF, name='default'),
  host(r'www', settings.ROOT_URLCONF, name='www'),
  host(r'api', 'api.urls', name='api'),
  host(r'api-dev', 'api.urls', name='api-dev'),
)