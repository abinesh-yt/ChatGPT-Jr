from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path(
        "chat/<int:chat_id>/",
        views.home,
        name="chat"
    ),

    path(
        "new-chat/",
        views.new_chat,
        name="new_chat"
    ),

    path(
        "delete-chat/<int:chat_id>/",
        views.delete_chat,
        name="delete_chat"
    ),

    path(
        "rename-chat/<int:chat_id>/",
        views.rename_chat,
        name="rename_chat"
    ),

    path(
        "send-message/<int:chat_id>/",
        views.send_message,
        name="send_message"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

]