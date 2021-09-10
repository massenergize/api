from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns(
  '',
  host(r'api', 'api.urls', name='api'),
  host(r'api-dev', 'api.urls', name='api-dev'),
  host(r'communities', settings.ROOT_URLCONF, name=settings.DEFAULT_HOST),
)