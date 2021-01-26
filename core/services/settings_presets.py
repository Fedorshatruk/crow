from ..models import GameSetting, Player

db_preset_1 = {
    'manufacturer_balance': 4000,
    'broker_balance': 8000,
    'crown_balance': 12000,
    'transaction_limit': 2000,
    'number_of_brokers': 3
}

db_preset_2 = {
    'manufacturer_balance': 6000,
    'broker_balance': 12000,
    'crown_balance': 12000,
    'transaction_limit': 2000,
    'number_of_brokers': 4
}

db_preset_3 = {
    'manufacturer_balance': 6000,
    'broker_balance': 12000,
    'crown_balance': 15000,
    'transaction_limit': 2000,
    'number_of_brokers': 5
}

db_preset_4 = {
    'manufacturer_balance': 6000,
    'broker_balance': 12000,
    'crown_balance': 18000,
    'transaction_limit': 2000,
    'number_of_brokers': 6
}

db_preset_5 = {
    'manufacturer_balance': 6000,
    'broker_balance': 12000,
    'crown_balance': 21000,
    'transaction_limit': 2000,
    'number_of_brokers': 7
}


def initialize_game_settings(session_id):
    """
    Инициализирует сет настроек в БД в зависимости от количества игроков в сессии
    :param session_id: id игровой сессии
    :return: создаёт экземпляр GameSetting в БД
    """
    # TODO Должна отрабатывать только при запуске игровой сессии

    # FIXME На данный момент к сессии может подключиться любое количество игроков
    number_of_players = Player.objects.filter(session_id=session_id).count()

    if 0 <= number_of_players <= 13:
        GameSetting.objects.create(**db_preset_1)

    elif number_of_players <= 20:
        GameSetting.objects.create(**db_preset_2)

    elif number_of_players <= 25:
        GameSetting.objects.create(**db_preset_3)

    elif number_of_players <= 30:
        GameSetting.objects.create(**db_preset_4)

    elif number_of_players <= 35:
        GameSetting.objects.create(**db_preset_5)

    elif number_of_players > 35:
        print('Достигнуто максимально возможное количество игроков в лобби!')
