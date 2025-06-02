from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from apps.chat.routing import websocket_urlpatterns

application = AuthMiddlewareStack(
    URLRouter(websocket_urlpatterns)
)
