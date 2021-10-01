from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns(
  '',
  host(r'api', 'api.urls', name='api'),
  host(r'api-dev', 'api.urls', name='api-dev'),
  host(r'api-canary', 'api.urls', name='api-canary'),
  host(r'communities', settings.ROOT_URLCONF, name=settings.DEFAULT_HOST),
  host(r'mc', '_main_.admin_urls', name='mc'),
  host(r'missioncontrol', '_main_.admin_urls', name='missioncontrol'),
  host(r'admin', '_main_.admin_urls', name='admin'),
)