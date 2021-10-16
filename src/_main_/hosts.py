from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns(
  '',
  host(r'api', 'api.urls', name='api'),
  host(r'api-dev', 'api.urls', name='api-dev'),
  host(r'api-canary', 'api.urls', name='api-canary'),
  host(r'communities', settings.ROOT_URLCONF, name=settings.DEFAULT_HOST),
  host(r'share', settings.ROOT_URLCONF, name='share'),
  host(r'mc', '_main_.admin_urls', name='missioncontrol'),
  host(r'mc-dev', '_main_.admin_urls', name='missioncontrol-dev'),
  host(r'mc-canary', '_main_.admin_urls', name='missioncontrol-canary'),
  host(r'djangoadmin', '_main_.admin_urls', name='djangoadmin'),
  host(r'djangoadmin-dev', '_main_.admin_urls', name='djangoadmin-dev'),
  host(r'djangoadmin-canary', '_main_.admin_urls', name='djangoadmin-canary'),
  host(r'cc', 'carbon_calculator.urls', name='carbon_calculator'),
  host(r'cc-dev', 'carbon_calculator.urls', name='carbon_calculator-dev'),
  host(r'cc-canary', 'carbon_calculator.urls', name='carbon_calculator-canary'),
)