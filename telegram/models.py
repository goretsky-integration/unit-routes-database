from django.db import models
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
