from django.urls import path

from . import views

app_name = "frontend"
urlpatterns = [
    path("", views.index, name="chat_home"),
    path("send/", views.chat_send, name="chat_send"),
]