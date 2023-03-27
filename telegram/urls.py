from django.urls import path

from telegram.views import TelegramChatsCreateListApi, TelegramChatByChatIdApi


urlpatterns = [
    path('', TelegramChatsCreateListApi.as_view()),
    path('<int:chat_id>/', TelegramChatByChatIdApi.as_view()),
]
