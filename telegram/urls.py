from django.urls import path, register_converter

from telegram.views import (
    TelegramChatsCreateListApi,
    TelegramChatByChatIdApi,
    TelegramChatTypesListApi,
)
from core.converters import AnyIntConverter

register_converter(AnyIntConverter, 'any_int')

urlpatterns = [
    path('', TelegramChatsCreateListApi.as_view()),
    path('chat-types/', TelegramChatTypesListApi.as_view()),
    path('<any_int:chat_id>/', TelegramChatByChatIdApi.as_view()),
]
