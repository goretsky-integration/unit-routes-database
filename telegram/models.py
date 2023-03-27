from django.db import models
from django.utils.translation import gettext as _

from scopes.models import ReportScope


class TelegramChat(models.Model):
    class ChatType(models.IntegerChoices):
        PRIVATE = 1, _('Private')
        GROUP = 2, _('Group')

    chat_id = models.BigIntegerField(db_index=True, unique=True)
    username = models.CharField(max_length=64, null=True, blank=True)
    title = models.CharField(max_length=64)
    type = models.PositiveSmallIntegerField(choices=ChatType.choices)
    report_scope = models.ForeignKey(
        ReportScope,
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return self.title
