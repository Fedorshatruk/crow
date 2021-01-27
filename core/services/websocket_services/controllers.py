import collections
import json

from django.db import models
from ...models import Session
from .websocket_serializers import WSSessionSerializer


def get_session_list_controller():
    queryset = Session.objects.exclude(status='Filled').annotate(players_quantity=models.Count('player'))
    data = WSSessionSerializer(queryset, many=True).data
    return data


def get_session_detail_controller(pk):
    queryset = Session.objects.filter(id=pk).annotate(players_quantity=models.Count('player'))
    data = WSSessionSerializer(queryset, many=True).data
    print(data)
    return data
