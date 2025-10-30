import datetime
import itertools
import logging
from collections.abc import Iterable
from dataclasses import dataclass

from django.conf import settings
from django.db.models import QuerySet
from django.db.utils import IntegrityError
from django.utils import timezone
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import (
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    InlineKeyboardButton,
)

from core.exceptions import AlreadyExistsError
from telegram.models import TelegramChat, TelegramMessage
from telegram.selectors import get_telegram_chats_by_chat_id


logger = logging.getLogger(__name__)


def update_telegram_chat(
    *,
    chat_id: int,
    title: str,
    username: str | None,
) -> int:
    telegram_chats = get_telegram_chats_by_chat_id(chat_id=chat_id)
    return telegram_chats.update(title=title, username=username)


def create_telegram_chat(
    *,
    chat_id: int,
    title: str,
    username: str | None,
    chat_type: TelegramChat.ChatType,
) -> TelegramChat:
    try:
        return TelegramChat.objects.create(
            chat_id=chat_id,
            title=title,
            username=username,
            type=chat_type,
        )
    except IntegrityError:
        raise AlreadyExistsError('Chat with provided chat ID already exists')


def get_telegram_bot() -> TeleBot:
    return TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


def get_pending_messages(*, limit: int = 10) -> QuerySet[TelegramMessage]:
    return TelegramMessage.objects.filter(
        sent_at__isnull=True,
        retries_count__gt=0,
        to_be_sent_at__lte=timezone.now(),
    ).order_by('to_be_sent_at', 'created_at')[:limit]


def create_telegram_text_message(
    bot_token: str,
    chat_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    to_be_sent_at: datetime.datetime | None = None,
) -> TelegramMessage:
    if reply_markup is not None:
        reply_markup = reply_markup.to_dict()
    if to_be_sent_at is None:
        to_be_sent_at = timezone.now()
    return TelegramMessage.objects.create(
        bot_token=bot_token,
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        to_be_sent_at=to_be_sent_at,
    )


def create_telegram_media_group_message(
    bot_token: str,
    chat_id: int,
    file_ids: Iterable[str],
    text: str | None = None,
    to_be_sent_at: datetime.datetime | None = None,
) -> list[TelegramMessage]:
    if to_be_sent_at is None:
        to_be_sent_at = timezone.now()
    file_ids = tuple(file_ids)
    if not file_ids:
        raise ValueError('At least one file ID is required')

    first_batch = file_ids[:10]
    remaining_file_ids = file_ids[10:]

    messages = [
        TelegramMessage(
            chat_id=chat_id,
            text=text,
            media_file_ids=first_batch,
            to_be_sent_at=to_be_sent_at,
        )
    ]
    for file_ids_batch in itertools.batched(remaining_file_ids, n=10):
        messages.append(
            TelegramMessage(
                chat_id=chat_id,
                media_file_ids=file_ids_batch,
                to_be_sent_at=to_be_sent_at,
            ),
        )
    return TelegramMessage.objects.bulk_create(messages)


@dataclass(frozen=True, slots=True, kw_only=True)
class TelegramMessageSender:
    message: TelegramMessage

    def get_media_file_ids(self) -> list[str] | None:
        if self.message.media_file_ids is None:
            return None
        return self.message.media_file_ids

    def get_media(self) -> list[InputMediaPhoto]:
        media = []
        file_ids = self.get_media_file_ids()

        if not file_ids:
            logger.error(
                'No media file IDs found for message ID %s',
                self.message.id,
            )
            return []
        if len(file_ids) > 10:
            logger.error(
                'Too many media file IDs (%s) for message ID %s, max is 10',
                len(file_ids),
                self.message.id,
            )
            file_ids = file_ids[:10]

        if self.message.text is not None:
            file_id, *file_ids = file_ids
            media.append(
                InputMediaPhoto(
                    media=file_id,
                    caption=self.message.text,
                    parse_mode='html',
                ),
            )
        media += [InputMediaPhoto(media=file_id) for file_id in file_ids]
        return media

    def get_reply_markup(self) -> InlineKeyboardMarkup | None:
        if self.message.reply_markup is None:
            return None
        rows = []
        for row in self.message.reply_markup.get('inline_keyboard', []):
            buttons = []
            for button in row:
                if 'url' in button and 'text' in button:
                    buttons.append(
                        InlineKeyboardButton(
                            url=button['url'],
                            text=button['text'],
                        ),
                    )
                elif 'callback_data' in button and 'text' in button:
                    buttons.append(
                        InlineKeyboardButton(
                            callback_data=button['callback_data'],
                            text=button['text'],
                        ),
                    )
            if buttons:
                rows.append(buttons)
        return InlineKeyboardMarkup(rows)

    def send_text_message(self) -> Message:
        return get_telegram_bot().send_message(
            chat_id=self.message.chat_id,
            text=self.message.text,
            reply_markup=self.get_reply_markup(),
        )

    def send_media_group_message(self) -> list[Message]:
        media = self.get_media()
        if not media:
            raise ValueError('No media to send')

        return get_telegram_bot().send_media_group(
            chat_id=self.message.chat_id,
            media=media,
        )

    def send(self) -> None:
        media_file_ids = self.get_media_file_ids()

        try:
            if media_file_ids:
                sent_messages = self.send_media_group_message()
            else:
                sent_message = self.send_text_message()
                sent_messages = [sent_message]
        except ApiTelegramException as error:
            self.message.retries_count -= 1
            self.message.error_message = str(error)
        else:
            self.message.sent_at = timezone.now()
            self.message.chat_message_ids = [
                msg.message_id for msg in sent_messages
            ]

        self.message.save()


def batch_create_telegram_messages(
    chat_ids: Iterable[int],
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    to_be_sent_at: datetime.datetime | None = None,
    media_file_ids: Iterable[str] | None = None,
) -> list[TelegramMessage]:
    if reply_markup is not None:
        reply_markup = reply_markup.to_dict()
    if to_be_sent_at is None:
        to_be_sent_at = timezone.now()
    extra_params = {}
    if media_file_ids is not None:
        extra_params['media_file_ids'] = list(media_file_ids)
    messages = [
        TelegramMessage(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            to_be_sent_at=to_be_sent_at,
            **extra_params,
        )
        for chat_id in chat_ids
    ]
    return TelegramMessage.objects.bulk_create(messages)
