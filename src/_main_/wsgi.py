# """
# WSGI config for massenergize_portal_backend project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
# """

# import os

# from django.core.wsgi import get_wsgi_application
# from channels.routing import ProtocolTypeRouter

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_main_.settings')

# # application = get_wsgi_application()
# application = ProtocolTypeRouter({
#     "http": get_wsgi_application()
# })
