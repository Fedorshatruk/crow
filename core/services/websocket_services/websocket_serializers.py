from rest_framework import serializers

from ...models import Session, GameSetting, Player


class WSGameSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSetting
        fields = ('crown_balance', )


class WSPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'nickname')


class WSSessionSerializer(serializers.ModelSerializer):
    '''Сериализатор для игор'''
    player = WSPlayerSerializer(many=True)
    players_quantity = serializers.IntegerField()
    settings = WSGameSettingSerializer()

    class Meta:
        model = Session
        fields = ("id", 'name', 'turn_count', 'settings', 'players_quantity', 'player')