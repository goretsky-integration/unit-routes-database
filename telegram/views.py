from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import LimitOffsetSerializer
from telegram.models import TelegramChat
from telegram.selectors import get_telegram_chats, get_telegram_chats_by_chat_id
from telegram.services import update_telegram_chat, create_telegram_chat


class TelegramChatTypesListApi(APIView):

    def get(self, request: Request):
        return Response(TelegramChat.ChatType.names)


class TelegramChatsCreateListApi(APIView):

    class InputSerializer(serializers.Serializer):
        chat_id = serializers.IntegerField()
        type = serializers.ChoiceField(TelegramChat.ChatType.names)
        title = serializers.CharField(max_length=64, min_length=1)
        username = serializers.CharField(
            allow_blank=True,
            allow_null=True,
            required=False,
            max_length=64,
            min_length=1,
        )

    def get(self, request: Request):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

        telegram_chats = get_telegram_chats(limit=limit, offset=offset)
        is_next_page_exists = get_telegram_chats(
            limit=1, offset=offset + limit,
        ).exists()

        response_data = {
            'telegram_chats': telegram_chats.values('title', 'chat_id'),
            'is_end_of_list_reached': not is_next_page_exists,
        }
        return Response(response_data)

    def post(self, request: Request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data
        create_telegram_chat(
            chat_id=serialized_data['chat_id'],
            title=serialized_data['title'],
            username=serialized_data['username'],
            chat_type=TelegramChat.ChatType[serialized_data['type']],
        )
        return Response(status=status.HTTP_201_CREATED)


class TelegramChatByChatIdApi(APIView):

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=64, min_length=1)
        username = serializers.CharField(
            allow_blank=True,
            allow_null=True,
            max_length=64,
            min_length=1,
        )

    class OutputSerializer(serializers.ModelSerializer):
        type = serializers.CharField(source='get_type_display')

        class Meta:
            model = TelegramChat
            fields = ('chat_id', 'username', 'title', 'type')

    def get(self, request: Request, chat_id: int):
        telegram_chat = get_telegram_chats_by_chat_id(chat_id).first()
        response_data = self.OutputSerializer(instance=telegram_chat).data
        return Response(response_data)

    def put(self, request: Request, chat_id: int):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data
        is_updated = update_telegram_chat(
            chat_id=chat_id,
            title=serialized_data['title'],
            username=serialized_data['username'],
        )
        response_status_code = (status.HTTP_204_NO_CONTENT if is_updated
                                else status.HTTP_404_NOT_FOUND)
        return Response(status=response_status_code)
