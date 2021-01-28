import collections
import json

from django.db import models
from ...models import Session, Player
from .websocket_serializers import WSSessionSerializer


def get_session_list_controller():
    queryset = Session.objects.exclude(status='Filled').annotate(players_quantity=models.Count('player'))
    data = WSSessionSerializer(queryset, many=True).data
    return data


def get_session_detail_controller(pk):
    queryset = Session.objects.filter(id=pk).annotate(players_quantity=models.Count('player'))
    data = WSSessionSerializer(queryset, many=True).data
    return data


def create_player(token: object, session_id: str):
    user = token.user
    session = Session.objects.filter(id=session_id).first()
    if user.player.all().count() == 0 or user.player.filter(session=session_id).count() == 0:
        Player.objects.create(nickname=user.username, user=user, session=session)
    print(session)
