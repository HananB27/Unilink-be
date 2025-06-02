import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Unilink_be.settings')

django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.chat.routing import websocket_urlpatterns  # This can now safely import models

from django.core.asgi import get_asgi_application
from Unilink_be.routing import application as websocket_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": websocket_application,  # ✅ plug in here
})
