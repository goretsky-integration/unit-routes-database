from fastapi import APIRouter, Depends, Query, Body, Response, status

from api import dependencies, schemas
from repositories import TelegramChatRepository

router = APIRouter(prefix='/telegram-chats', tags=['Telegram Chat'])


@router.get(
    path='/{chat_id}/',
)
def get_telegram_chat_by_chat_id(
        chat_id: int = Query(),
        telegram_chats: TelegramChatRepository = Depends(dependencies.get_telegram_chats_repository),
) -> schemas.TelegramChat:
    return telegram_chats.get_by_chat_id(chat_id=chat_id)


@router.put(
    path='/{chat_id}/',
)
def update_telegram_chat_by_chat_id(
        chat_id: int = Query(),
        telegram_chat: schemas.TelegramChatToUpdate = Body(),
        telegram_chats: TelegramChatRepository = Depends(dependencies.get_telegram_chats_repository),
):
    telegram_chats.update_by_chat_id(chat_id=chat_id, title=telegram_chat.title)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
