"""
ASGI config for AI_quiz project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# default lines, kept but deactivated
# import os
# from django.core.asgi import get_asgi_application

# application = get_asgi_application()


import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import multiplayer.routing  # Your app's routing file

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_quiz.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles standard HTTP requests
    "websocket": AuthMiddlewareStack(  # Handles WebSocket connections
        URLRouter(
            multiplayer.routing.websocket_urlpatterns
        )
    ),
})
