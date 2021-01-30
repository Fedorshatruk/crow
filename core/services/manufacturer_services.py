"""
Лимит сделки должнен учитываться только при одобрении сделки маклером.
Сделки, использованные в пересчёте, должны быть взяты только для i-го хода.
"""


class InvalidBilletAmountException(Exception):
    """Ошибка для некорректно введённых расчётных данных"""
    def __init__(self, message='Ошибка в количестве производимых заготовок!'):
        self.message = message
        super().__init__(self.message)


def count_costs_fixed(billets):
    """Возвращает величину постоянных затрат в зависимости от количества произведённых заготовок.
    Выбрасывает InvalidBilletAmountException, если на вход подаётся некорректное значение"""

    if billets < 0 or type(billets) is not int:
        raise InvalidBilletAmountException

    if billets <= 10:
        return 600
    elif billets <= 20:
        return 1000
    elif billets <= 30:
        return 1400
    elif billets <= 50:
        return 2000
    elif billets <= 100:
        return 4000


def count_costs_variable(billets):
    """Возвращает величину переменных затрат в зависимости от количества произведённых заготовок.
    Выбрасывает InvalidBilletAmountException, если на вход подаётся некорректное значение"""

    if billets < 0 or type(billets) is not int:
        raise InvalidBilletAmountException

    if 0 <= billets <= 10:
        return 80 * billets
    elif billets <= 20:
        return 70 * billets
    elif billets <= 30:
        return 55 * billets
    elif billets <= 50:
        return 40 * billets
    elif billets <= 100:
        return 30 * billets


def count_costs_materials(billets):
    """Возвращает величину затрат на материалы в зависимости от количества произведённых заготовок.
    Выбрасывает InvalidBilletAmountException, если на вход подаётся некорректное значение"""

    if billets < 0 or type(billets) is not int:
        raise InvalidBilletAmountException

    costs_raw_materials_single = 30
    return billets * costs_raw_materials_single


def count_costs_negotiation(number_of_transactions):
    """Возвращает величину затрат на переговоры в зависимости от их количества"""
    costs_negotiation_single = 20

    if number_of_transactions < 0 or type(number_of_transactions) is not int:
        raise Exception('Неверное количество проведённых производителем транзакций')

    return number_of_transactions * costs_negotiation_single





def count_manufacturers(session_id: int, turn_id: int, player, warehouse):
    """
    Функция просчитывает игровые параметры для производителей и записывает новые параметры в БД.
    :param session_id: id игровой сессии
    :param turn_id: id хода. необходим для учёта транзакций только на текущем ходу
    :return: обновляет игровые параметры производителей
    """

    manufacturers = player.objects.filter(session_id=session_id, role='manufacturer', is_bankrupt=False)

    for manufacturer in manufacturers:
        try:
            billets_produced = manufacturer.production.billets_produced
        except:
            billets_produced = 0
        warehousing = warehouse.objects.filter(player_id=manufacturer.id).first()
        try:
            billets_stored = warehousing.billets
        except AttributeError:
            warehousing = warehouse.objects.create(player_id=manufacturer.id)
            warehousing.save()
            billets_stored = warehousing.billets
        transactions = manufacturer.transaction_m.filter(turn_id=turn_id, approved_by_broker=True)
        transaction_count = transactions.count()

        costs_fixed = count_costs_fixed(billets_produced)
        print(costs_fixed)
        costs_variable = count_costs_variable(billets_produced)
        print(costs_variable)
        costs_materials = count_costs_materials(billets_produced)
        print(costs_materials)
        costs_production = costs_fixed + costs_variable + costs_materials

        balance_update_1 = manufacturer.balance - costs_production

        if balance_update_1 < 0:
            manufacturer.is_bankrupt = True
            print(f'{manufacturer.nickname}, Вы не смогли оплатить издержки и расходы на сырьё')
            manufacturer.save()
            continue

        billets_sold, billet_price, billet_transporting = [], [], []
        costs_transporting = 10

        for transaction in transactions:

            billets_sold.append(transaction.number_of_billets)
            billet_price.append(transaction.billet_price)
            billet_transporting.append(transaction.costs_transporting_single)

        for i in range(transaction_count):
            costs_transporting += billets_sold[i] * billet_transporting[i]

        costs_negotiation = count_costs_negotiation(transaction_count)

        balance_update_2 = balance_update_1 - costs_negotiation - costs_transporting

        if balance_update_2 < 0:
            manufacturer.is_bankrupt = True
            print(f'{manufacturer.nickname}, Вы не смогли оплатить расходы на переговоры и логистику')
            manufacturer.save()
            continue

        if sum(billets_sold) > billets_produced + billets_stored:
            manufacturer.is_bankrupt = True
            print(f'{manufacturer.nickname}, Вы пытались продать больше заготовок, чем у вас имеется.'
                  'Корона посчитала вас недобросовестным и объявила банкротом')
            manufacturer.save()
            continue

        proceeds = 0
        for i in range(transaction_count):
            proceeds += billets_sold[i] + billet_price[i]

        balance_update_3 = balance_update_2 + proceeds

        billets_left = billets_produced + billets_stored - sum(billets_sold)

        costs_storage_single = 50
        costs_storage = costs_storage_single * billets_left

        balance_update_4 = balance_update_3 - costs_storage

        if balance_update_4 < 0:
            manufacturer.is_bankrupt = True
            print(f'{manufacturer.nickname}, Вы не смогли оплатить расходы на хранение заготовок.')
            manufacturer.save()
            continue

        manufacturer.balance = balance_update_4
        warehousing.billets = billets_left

        manufacturer.save()
        warehousing.save()

        print(f'Сделки Игрока {manufacturer.nickname} совершены успешно!. '
              f'Баланс на начало следующего хода равен {manufacturer.balance} песо. '
              f'На складе осталось {warehousing.billets} заготовок')