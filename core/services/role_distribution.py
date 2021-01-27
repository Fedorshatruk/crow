from ..models import Player, Session


def distribute_roles(session_id):
    """ Распределяет роли между игроками в зависимости от количества игроков в активной сессии"""
    number_of_brokers = Session.
