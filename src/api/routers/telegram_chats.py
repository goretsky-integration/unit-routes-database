from fastapi import APIRouter, Depends, Query, Body, Response, status

from api import dependencies, schemas
from repositories import TelegramChatRepository

router = APIRouter(prefix='/telegram-chats', tags=['Telegram Chat'])


@router.get(
    path='/',
    response_model=schemas.TelegramChatsListPage,
)
def get_telegram_chats(
        limit: int = Query(default=100, le=100, ge=1),
        offset: int = Query(default=0, ge=0, le=10_000_000_000),
        telegram_chats: TelegramChatRepository = Depends(dependencies.get_telegram_chats_repository),
):
    telegram_chats_list_page = telegram_chats.get_all(limit=limit, offset=offset)
    telegram_chats_list_next_page = telegram_chats.get_all(limit=1, offset=offset + limit)
    is_end_of_list_reached = not telegram_chats_list_next_page
    return {
        'telegram_chats': telegram_chats_list_page,
        'is_end_of_list_reached': is_end_of_list_reached,
    }


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
