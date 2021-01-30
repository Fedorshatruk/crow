from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from rest_framework.authtoken.models import Token

from .services.websocket_services.controllers import get_session_list_controller, get_session_detail_controller, \
    create_player, delete_player


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'game'
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json
        if message['type'] == 'get_games':
            self.send(json.dumps(get_session_list_controller()))
        elif message['type'] == 'change_db':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'send_game_data',
                    'message': message
                }
            )

    def send_game_data(self, _):
        data = get_session_list_controller()
        self.send(text_data=json.dumps(
            data
        ))


class SessionDetailConsumer(WebsocketConsumer):
    def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.user_token = self.scope['url_route']['kwargs']['token']
        self.room_group_name = f'session_{self.session_id}'
        self.token = Token.objects.filter(key=self.user_token).first()
        if self.token:
            create_player(self.token, self.session_id)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        delete_player(self.token, self.session_id)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # TODO проработать изменения состояния для каждого пользователя
        text_data_json = json.loads(text_data)
        message = text_data_json
        if message['type'] == 'send_detail_data':
            self.send({'type': 'send_detail_data', 'session_id': message['session_id']})
        elif message['type'] == 'GetDetailData':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'send_detail_data',
                    'session_id': message['session_id']
                }
            )

    def send_detail_data(self, event):
        pk = int(event['session_id'])
        data = get_session_detail_controller(pk)
        self.send(text_data=json.dumps(
            data[0]
        ))


class UserConsumer(WebsocketConsumer):
    def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'session_{self.session_id}_user_{self.user_id}'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        print('UserConsumer')
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json
        if message['type'] == 'send_detail_data':
            self.send({'type': 'send_detail_data', 'session_id': message['session_id']})
        elif message['type'] == 'GetDetailData':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'send_detail_data',
                    'session_id': message['session_id']
                }
            )

    def send_detail_data(self, event):
        pk = int(event['session_id'])
        data = get_session_detail_controller(pk)
        self.send(text_data=json.dumps({
            'type': 'send_detail_data',
            'data': data
        }))

