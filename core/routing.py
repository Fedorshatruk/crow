from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/user/(?P<session_id>\w+)/(?P<user_id>\w+)/$', consumers.UserConsumer.as_asgi()),
    re_path(r'ws/detail/(?P<session_id>\w+)/(?P<token>\w+)/$', consumers.SessionDetailConsumer.as_asgi()),
    re_path(r'ws/session/', consumers.GameConsumer.as_asgi()),
]