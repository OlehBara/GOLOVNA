from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/support/", consumers.SupportChatConsumer.as_asgi()),
]
