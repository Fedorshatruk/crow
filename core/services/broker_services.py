# from ..models import Player, Transaction

costs_fixed = 1000


def count_brokers(session_id: int, turn_id: int, player, transaction):
    """
    Функция просчитывает игровые параметры маклеров и записывает новые параметры в БД.
    :param session_id: id игровой сессии
    :param turn_id: номер игрового хода. параметр нужен для подсчёта рыночного объёма заготовок
    :return: обновляет игровые параметры маклеров
    """

    market_billets_count = 0
    market_transactions = transaction.objects.filter(turn_id=turn_id)
    brokers = player.objects.filter(session_id=session_id, role='broker', is_bankrupt=False)

    for transaction in market_transactions:
        market_billets_count += transaction.number_of_billets

    crown_balance = 12000

    try:
        market_billet_price = int(crown_balance / market_billets_count)
    except ZeroDivisionError:
        market_billet_price = 160

    for broker in brokers:

        transactions = broker.transaction_b.filter(turn_id=turn_id, approved_by_broker=True)
        costs_purchase = 0
        billets_bought = 0

        for transaction in transactions:
            billets_bought += transaction.number_of_billets
            costs_purchase += transaction.number_of_billets * transaction.billet_price

        balance_updated_1 = broker.balance - costs_purchase

        if balance_updated_1 < 0:
            broker.is_bankrupt = True
            print(f'{broker.nickname}, Вы не смогли оплатить заказанные заготовки!')
            broker.save()
            continue

        balance_updated_2 = balance_updated_1 - costs_fixed

        if balance_updated_2 < 0:
            broker.is_bankrupt = True
            print(f'{broker.nickname}, Вам не хватило средств на доставку товара Короне!')
            broker.save()
            continue

        balance_updated_3 = balance_updated_2 + billets_bought * market_billet_price

        broker.balance = balance_updated_3
        broker.save()

        print(f'Сделки брокера {broker.nickname} прошли успешно! Баланс на следующий ход: {broker.balance}')
