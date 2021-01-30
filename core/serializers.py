from rest_framework.serializers import ModelSerializer

from .models import GameSetting, MainUser, Transaction, Session, Player, Production, Warehouse


class MainUserListSerializer(ModelSerializer):
    class Meta:
        model = MainUser
        fields = ('id', 'username')


class MainUserDetailSerializer(ModelSerializer):
    class Meta:
        model = MainUser
        fields = ('username',)


class GameSettingSerializer(ModelSerializer):
    class Meta:
        model = GameSetting
        fields = "__all__"


class TransactionSerializer(ModelSerializer):

    class Meta:
        model = Transaction
        fields = "__all__"


class SessionSerializer(ModelSerializer):

    class Meta:
        model = Session
        fields = ('name', 'turn_count', 'status', 'is_started')


class PlayerSerializer(ModelSerializer):

    class Meta:
        model = Player
        exclude = ("balance",)


class ProductionSerializer(ModelSerializer):

    class Meta:
        model = Production
        fields = '__all__'


class WarehouseSerializer(ModelSerializer):

    class Meta:
        model = Warehouse
        fields = '__all__'
