from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from .models import GameSetting, MainUser, Transaction, Session, Player, Production, Warehouse
from .serializers import GameSettingSerializer, MainUserDetailSerializer, \
    TransactionSerializer, SessionSerializer, PlayerSerializer, ProductionSerializer, WarehouseSerializer


class GameSettingViewSet(ModelViewSet):
    """Вывод настроек игры"""
    # FIXME посмотреть get serializer
    queryset = GameSetting.objects.all()
    serializer_class = GameSettingSerializer


class SessionViewSet(ModelViewSet):
    """Вывод игровых ссесий"""
    queryset = Session.objects.exclude(status='Filled')
    serializer_class = SessionSerializer
    permission_classes = [IsAdminUser,]


class UserViewSet(ModelViewSet):
    """Вывод пользвателей"""
    queryset = MainUser.objects.all()
    serializer_class = MainUserDetailSerializer


class TransactionViewSet(ModelViewSet):
    """Вывод транзакций"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class PlayerViewSet(ModelViewSet):
    """Вывод игроков"""
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class ProductionViewSet(ModelViewSet):
    # FIXME я хуй знает что сдесь написать
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer


class WarehouseViewSet(ModelViewSet):
    """Вывод складов пользователей"""
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class TurnViewSet(ModelViewSet):
    """Вывод шагов"""
    # FIXME ждем исправлений от Димона
    pass
