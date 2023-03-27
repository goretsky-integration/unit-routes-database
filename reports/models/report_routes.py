from django.db import models

from reports.models.report_types import ReportType
from telegram.models import TelegramChat
from units.models import Unit


class ReportRoute(models.Model):
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    telegram_chat = models.ForeignKey(TelegramChat, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('report_type', 'unit', 'telegram_chat')
