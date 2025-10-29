from django.db import models
from django.utils import timezone
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from user_roles.models import UserRole


class TelegramChat(models.Model):
    class ChatType(models.IntegerChoices):
        PRIVATE = (
            1,
            capfirst(_('telegram|model|telegram_chat|chat_type|private')),
        )
        GROUP = (
            2,
            capfirst(_('telegram|model|telegram_chat|chat_type|group')),
        )

    chat_id = models.BigIntegerField(
        db_index=True,
        unique=True,
        verbose_name=_('telegram|model|telegram_chat|chat_id'),
    )
    username = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('telegram|model|telegram_chat|username'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('telegram|model|telegram_chat|title'),
    )
    type = models.PositiveSmallIntegerField(
        choices=ChatType.choices,
        verbose_name=capfirst(_('telegram|model|telegram_chat|type')),
    )
    role = models.ForeignKey(
        to=UserRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=capfirst(_('telegram|model|telegram_chat|role')),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('telegram|model|telegram_chat|created_at'),
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('telegram|model|telegram_chat')
        verbose_name_plural = _('telegram|model|telegram_chats')


class TelegramMessage(models.Model):
    chat_id = models.BigIntegerField(
        verbose_name=_('Chat ID'),
    )
    chat_message_ids = models.JSONField(
        verbose_name=_('Chat message IDs'),
        help_text=_('Id of message in chat, returned by Telegram API'),
        null=True,
        blank=True,
    )
    text = models.TextField(
        max_length=4096,
        verbose_name=_('Message text'),
        null=True,
        blank=True,
    )
    media_file_ids = models.JSONField(
        verbose_name=_('Media file IDs'),
        null=True,
        blank=True,
    )
    error_message = models.CharField(
        verbose_name=_('Error message'),
        max_length=4096,
        null=True,
        blank=True,
    )
    retries_count = models.PositiveIntegerField(
        verbose_name=_('Retries left'),
        default=5,
    )
    to_be_sent_at = models.DateTimeField(
        verbose_name=_('To be sent at'),
        help_text=_('The time at which the message was sent.'),
        default=timezone.now,
    )
    sent_at = models.DateTimeField(
        verbose_name=_('Sent at'),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name=_('Updated at'),
        auto_now=True,
    )
    reply_markup = models.JSONField(
        verbose_name=_('Reply markup'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Telegram message')
        verbose_name_plural = _('Telegram messages')
        ordering = ('-created_at',)
        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(text__isnull=False)
                    | models.Q(media_file_ids__isnull=False)
                ),
                name='text_or_media_file_ids_not_null',
                violation_error_message=_(
                    'Either text or media file IDs must be set.',
                ),
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(media_file_ids__isnull=True)
                    | models.Q(reply_markup__isnull=True)
                ),
                name='media_file_ids_and_reply_markup_not_both_set',
                violation_error_message=_(
                    'Reply markup can be set only for text messages.',
                ),
            ),
        )
