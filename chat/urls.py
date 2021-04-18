from django.urls import path

from . import views

urlpatterns = [
    path('',views.index),
    path('chat/<str:room_name>/',views.room,name='room'),
    
]