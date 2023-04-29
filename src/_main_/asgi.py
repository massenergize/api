
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from socket_notifications.routing import websocket_urls
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_main_.settings')

application = ProtocolTypeRouter({
    "http":get_asgi_application(), 
    "websocket":AuthMiddlewareStack(URLRouter(websocket_urls))
})
