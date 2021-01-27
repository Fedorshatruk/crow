from ..models import Player, Session
import random


def distribute_roles(session_id):
    """ Распределяет роли между игроками в зависимости от количества игроков в активной сессии"""
    players_in_session = Player.objects.filter(session_id=session_id)
    session_settings = Session.objects.get(pk=session_id).settings

    broker_players = random.sample(list(players_in_session), session_settings.number_of_brokers)

    for player in broker_players:
        player.role = 'broker'
        player.save()

    for player in players_in_session:
        if player.role == 'broker':
            continue

        player.role = 'manufacturer'
        player.save()
