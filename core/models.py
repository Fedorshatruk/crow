from django.contrib.auth.models import AbstractUser
from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_sok_get_games():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("game", {"type": "send_game_data"})


def send_sok_change_session_id(session_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"session_{session_id}",
                                            {"type": "send_detail_data", 'pk': f'{session_id}'})

CITIES = (
    ('NF', "Неверфол"),
    ('TT', "Тортуга"),
    ('WS', "Вемшир"),
    ('AV', "Айво"),
    ('AD', "Алендор"),
    ('ET', "Этруа"),)

CREATED = 'Created'
FILLED = 'Filled'

SESSION_STATUS = (
    (CREATED, "Сессия создана"),
    (FILLED, "Сессия заполнена"),
)

BROKER = 'broker'
MANUFACTURER = 'manufacturer'

ROLES = (
    (BROKER, 'Маклер'),
    (MANUFACTURER, 'Производитель'),
)

turn_time_default = {
    1: 15,
    2: 10,
    3: 10,
    4: 10,
    5: 7,
    6: 7,
    7: 7,
    8: 7,
    9: 7,
    10: 7
}


class MainUser(AbstractUser):
    """Модель пользователя платформы"""

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# FIXME Значения настроек должны быть строгими и зависеть от количества игроков в лобби
# Скорее всего, мы их сделаем сами ручками и впоследствии трогать не будем
class GameSetting(models.Model):
    """Модель пресета настроек игры"""
    manufacturer_balance = models.PositiveIntegerField(verbose_name='Баланс производителя')
    broker_balance = models.PositiveIntegerField(verbose_name="Баланс маклера")
    crown_balance = models.PositiveIntegerField(verbose_name="Баланс короны", default=12000)
    transaction_limit = models.PositiveIntegerField(verbose_name="Лимит сделки")
    number_of_brokers = models.PositiveIntegerField(verbose_name='Количество маклеров в сессии', default=3)
    turn_time_preset = models.TextField(default=turn_time_default)  # JSONField; ячейка должна хранить словарь с временами ходов

    def __str__(self):
        return f'Сет настроек {self.pk}'

    class Meta:
        verbose_name = 'Пресет настроек'
        verbose_name_plural = 'Пресеты настроек'


class Session(models.Model):
    """Модель игровой сессии"""

    name = models.CharField(max_length=255, verbose_name='Название сессии')
    turn_count = models.PositiveIntegerField(verbose_name='Количество игровых ходов')
    settings = models.ForeignKey(GameSetting, related_name='session', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=100, choices=SESSION_STATUS, verbose_name='Статус сессии', default='Created')
    is_started = models.BooleanField(default=False)
<<<<<<< HEAD
=======
    player_count = models.IntegerField(verbose_name="количество игроков", default=14)
>>>>>>> a14be9c7d87c8373fb1f7ec39c486c021e0eff1f

    def __str__(self):
        return f'Сессия "{self.name}"'

    class Meta:
        verbose_name = 'Игровая сессия'
        verbose_name_plural = 'Игровые сессии'

    def get_broker_balance(self):
        return self.settings.broker_balance

    def get_manufacturer_balance(self):
        return self.settings.manufacturer_balance

    def save(self, *args, **kwargs):
        create_turn = True if not self.pk else False
        super().save(*args, **kwargs)
        if create_turn:
            for i in range(self.turn_count):
                Turn.objects.create(
                    turn_num=i + 1,
                    session=self
                )
        send_sok_get_games()
        send_sok_change_session_id(self.pk)

    def delete(self, *args, **kwargs):
        super().save(*args, **kwargs)
        send_sok_get_games()


class State(models.Model):
    """Модель состояния игровой сессии"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='state')
    turn = models.PositiveIntegerField()
    game_state = models.TextField()  # JSONField


class Player(models.Model):
    """Модель игрока в игровой сессии"""

    nickname = models.CharField(max_length=255, verbose_name='Никнейм', default='')
    user = models.ForeignKey(MainUser, on_delete=models.CASCADE, related_name='player')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, related_name='player', null=True)
    city = models.CharField(max_length=10, choices=CITIES, verbose_name='Город', null=True)
    role = models.CharField(max_length=20, choices=ROLES, verbose_name='Игровая роль', blank=True, default='')
    balance = models.IntegerField(default=0)
    is_bankrupt = models.BooleanField(default=False)
    turn_finished = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.nickname} в городе {self.city}'

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def save(self, *args, **kwargs):
        send = False
        if self.session.status == 'Created':
            if not self.role:
                send = True
            else:
                if self.role == 'broker':
                    self.balance = self.session.settings.broker_balance
                else:
                    self.balance = self.session.settings.manufacturer_balance
        super().save(*args, **kwargs)
        if self.session.player_count == self.session.player.all().count():
            session = self.session
            session.status = FILLED
            session.save()
        if self.is_bankrupt:
            pass # место для сокета
        if self.turn_finished:
            pass

        if send:
            send_sok_get_games()


class Production(models.Model):
    """Модель запроса на производство"""
    manufacturer = models.ForeignKey(Player,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     related_name='production',
                                     limit_choices_to={'role': 'manufacturer'})
    billets_produced = models.PositiveIntegerField()

    def __str__(self):
        return f'Запрос на производство игрока {self.manufacturer}'

    class Meta:
        verbose_name = 'Запрос на производство'
        verbose_name_plural = 'Запросы на производство'


class Warehouse(models.Model):
    """Модель склада производителей"""
    player = models.ForeignKey(Player,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='warehouse',
                               limit_choices_to={'role': 'manufacturer'})
    billets = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Склад игрока {self.player}'


class Turn(models.Model):
    """Модель хода"""
    turn_num = models.IntegerField(verbose_name='Номер хода')
    session = models.ForeignKey(Session, verbose_name='Сессия', on_delete=models.CASCADE, related_name='turn')
    turn_time = models.PositiveIntegerField(verbose_name='Время хода', blank=True, default=30)

    # FIXME состакать с таймером
    turn_finished = models.BooleanField(default=False)

    def __str__(self):
        return f'Ход № {self.turn_num} Сессия №{self.session} {self.pk}'

    class Meta:
        verbose_name = 'Ход'
        verbose_name_plural = 'Ходы'
<<<<<<< HEAD
=======

    def save(self, *args, **kwargs):
        super(Turn, self).save(*args, **kwargs)
>>>>>>> a14be9c7d87c8373fb1f7ec39c486c021e0eff1f


class Transaction(models.Model):
    """Модель транзакции"""
    manufacturer = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transaction_m',
                                     limit_choices_to={'role': 'manufacturer'})
    broker = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transaction_b',
                               limit_choices_to={'role': 'broker'})
    number_of_billets = models.PositiveIntegerField(verbose_name='Количество')
    billet_price = models.PositiveIntegerField(verbose_name="Цена за заготовку")
    costs_transporting_single = models.PositiveIntegerField(default=10)
    approved_by_broker = models.BooleanField(default=False)
<<<<<<< HEAD
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE, related_name='transaction', default='')
=======
    # FIXME Поменял ссылку на номер хода с отдельной модели на ссылку статуса сессии
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE, related_name='transaction', default='', null=True)
>>>>>>> a14be9c7d87c8373fb1f7ec39c486c021e0eff1f

    def __str__(self):
        return f'Сделка между {self.manufacturer} и {self.broker} на {self.turn} ходу'

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'

    def save(self, *args, **kwargs):
        print(Turn.objects.exclude(turn_finished=True).filter(session=self.broker.session).first())
        self.turn = Turn.objects.exclude(turn_finished=True).filter(session=self.broker.session).first()
        super().save(*args, **kwargs)


class UserWebSocket(models.Model):
    user = models.ForeignKey(MainUser, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=255)
