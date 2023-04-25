from django.urls import re_path

from socket_notifications.consumers.user_session_tracker_consumer import UserSessionTrackerConsumer


websocket_urls = [
    re_path(r'ws/me-client/connect/', UserSessionTrackerConsumer.as_asgi()),
]

