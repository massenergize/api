from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns(
  '',
  host(r'search', settings.ROOT_URLCONF, name='www'),
  host(r'admin', settings.ROOT_URLCONF, name='admin'),
  host(r'^', settings.ROOT_URLCONF, name='api'),
)