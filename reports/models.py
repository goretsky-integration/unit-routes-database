from django.db import models

from telegram.models import TelegramChat
from units.models import Unit


class ReportType(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    verbose_name = models.CharField(max_length=64)
    parent = models.ForeignKey(
        to='ReportType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.verbose_name


class ReportRoute(models.Model):
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    telegram_chat = models.ForeignKey(TelegramChat, on_delete=models.CASCADE)
