import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message,Room
from django.contrib.auth.models import User

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self,data=None):
        print("Fetch Messages")
        messages=reversed(Message.last_10_messages(self.room))
        content={
            'command':'messages',
            'messages':self.messages_to_json(messages)
        }
        self.send_message(content)


    def new_message(self,data):
        print("New Messages")
        author=data['from']
        author_user=User.objects.filter(username=author)[0]
        print(data['message'])
        message=Message.objects.create(
            author=author_user,
            content=data['message'],
            room_name=self.room
        )
        content={
            'command':'new_message',
            'message':self.message_to_json(message)
        }
        print(message.author.username)
        return self.send_chat_message(content)

    def messages_to_json(self,messages):
        result=[]
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self,message):
        return {
            'author':message.author.username,
            'content':message.content,
            'timestamp':str(message.timestamp),
            'room':message.room_name.room_name
        }

    commands={
        'fetch_messages':fetch_messages,
        'new_message':new_message
    }

    def connect(self):
        print('Connected')
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room, self.create = Room.objects.get_or_create(room_name=self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        print("DisConnected")
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None):
        print("Received")

        data = json.loads(text_data)
        self.commands[data['command']](self,data)


    def send_chat_message(self,message):
        # Send message to room group
        print("Send Chat Message")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self,message):
        print("Send Message")
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        print("Chat Message")
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))