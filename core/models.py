from django.contrib.auth.models import AbstractUser
from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .services.broker_services import count_brokers
from .services.manufacturer_services import count_manufacturers
from random import choices
from countdowntimer_model.models import CountdownTimer
from .services.timer import set_turn_timers


def send_sok_get_games():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("game", {"type": "send_game_data"})


def send_sok_change_session_id(session_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"session_{session_id}",
                                            {"type": "send_detail_data", 'session_id': f'{session_id}'})


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


class MainUser(AbstractUser):
    """Модель пользователя платформы"""

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class TurnCountdownTimer(CountdownTimer):
    def __str__(self):
        return f'Таймер {self.pk}'


class GameSetting(models.Model):
    """Модель пресета настроек игры"""
    manufacturer_balance = models.PositiveIntegerField(verbose_name='Баланс производителя')
    broker_balance = models.PositiveIntegerField(verbose_name="Баланс маклера")
    crown_balance = models.PositiveIntegerField(verbose_name="Баланс короны", default=12000)
    transaction_limit = models.PositiveIntegerField(verbose_name="Лимит сделки")
    number_of_brokers = models.PositiveIntegerField(verbose_name='Количество маклеров в сессии', default=3)

    def __str__(self):
        return f'Сет настроек {self.pk}'

    class Meta:
        verbose_name = 'Пресет настроек'
        verbose_name_plural = 'Пресеты настроек'


class Session(models.Model):
    """Модель игровой сессии"""

    name = models.CharField(max_length=255, verbose_name='Название сессии')
    turn_count = models.PositiveIntegerField(verbose_name='Количество игровых ходов')
    settings = models.OneToOneField(GameSetting,
                                    related_name='session',
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    default=None)
    status = models.CharField(max_length=100, choices=SESSION_STATUS, verbose_name='Статус сессии', default='Created')
    is_started = models.BooleanField(default=False)
    player_count = models.IntegerField(verbose_name="количество игроков", default=14)

    def __str__(self):
        return f'Сессия "{self.name}" {self.pk}'

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
    city = models.CharField(max_length=10, choices=CITIES,
                            verbose_name='Город',
                            null=True,
                            default=choices(CITIES)[0][0]
                            )
    role = models.CharField(max_length=20, choices=ROLES,
                            verbose_name='Игровая роль', blank=True,
                            default=''
                            )
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
        if self.session.status == CREATED or self.session.status == FILLED and not self.session.is_started:
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
            if self.session.player.filter(turn_finished=False, is_bankrupt=False).all().count() == 0:
                obj = Turn.objects.exclude(turn_finished=True).filter(session=self.session).first()
                obj.turn_finished = True
                obj.save()

        if send:
            send_sok_get_games()


class Production(models.Model):
    """Модель запроса на производство"""
    manufacturer = models.OneToOneField(Player,
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
    player = models.OneToOneField(Player,
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
    timer = models.OneToOneField(TurnCountdownTimer, verbose_name='Таймер хода',
                                 on_delete=models.SET_NULL,
                                 related_name='turn',
                                 null=True)

    # FIXME состакать с таймером
    turn_finished = models.BooleanField(default=False)

    def __str__(self):
        return f'Ход № {self.turn_num} Сессия №{self.session} {self.pk}'

    class Meta:
        verbose_name = 'Ход'
        verbose_name_plural = 'Ходы'

    def save(self, *args, **kwargs):
        count_brokers(self.session.pk, self.pk, Player, Transaction)
        count_manufacturers(self.session.pk, self.pk, Player, Warehouse)
        super(Turn, self).save(*args, **kwargs)


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
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE, related_name='transaction', default='')

    def __str__(self):
        return f'Сделка между {self.manufacturer} и {self.broker} на {self.turn} ходу'

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'

    def save(self, *args, **kwargs):
        self.turn = Turn.objects.exclude(turn_finished=True).filter(session=self.broker.session).first()
        super().save(*args, **kwargs)


class UserWebSocket(models.Model):
    user = models.ForeignKey(MainUser, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=255)
