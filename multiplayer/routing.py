from django.urls import re_path
from .consumers import ChatConsumer
import re

websocket_urlpatterns = [
    re_path(r"game-room/.*", ChatConsumer.as_asgi()),
]