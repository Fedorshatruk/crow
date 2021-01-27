from django.contrib import admin

from .models import MainUser, TurnCountdownTimer, GameSetting, Transaction, Session, Player, Production, Turn, Warehouse, UserWebSocket

admin.site.register(MainUser)
admin.site.register(GameSetting)
admin.site.register(Transaction)
admin.site.register(Session)
admin.site.register(Player)
admin.site.register(Production)
admin.site.register(Turn)
admin.site.register(Warehouse)
admin.site.register(UserWebSocket)
admin.site.register(TurnCountdownTimer)

