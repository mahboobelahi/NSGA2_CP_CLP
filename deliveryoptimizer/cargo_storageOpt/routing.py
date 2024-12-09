from django.urls import re_path
from .import consumers 

websocket_urlpatterns = [
    re_path(r'ws/flag/$', consumers.FlagConsumer.as_asgi()),  # WebSocket route
    re_path(r'ws/ar/$', consumers.ARConsumer.as_asgi()),
    re_path(r'ws/flag-spin/$', consumers.SpinFlagConsumer.as_asgi()),
]
