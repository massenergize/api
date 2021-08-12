from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns(
  '',
  host(r'search', 'website.urls', name='search'),
  host(r'share', 'website.urls', name='share'),
  host(r'admin', settings.ROOT_URLCONF, name='admin'),
  host(r'^api', settings.ROOT_URLCONF, name='api'),
)