from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    room_name=models.CharField(max_length=50)

    def __str__(self):
        return self.room_name


class Message(models.Model):
    author=models.ForeignKey(User,related_name='author_message',on_delete=models.CASCADE)
    room_name=models.ForeignKey(Room,on_delete=models.CASCADE)
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.author.username

    def last_10_messages(room):
        return Message.objects.order_by('-timestamp').filter(room_name=room)[:100]



