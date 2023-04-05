from django.db import models
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from reports.models.report_types import ReportType
from telegram.models import TelegramChat
from units.models import Unit


class ReportRoute(models.Model):
    report_type = models.ForeignKey(
        to=ReportType,
        on_delete=models.CASCADE,
        verbose_name=capfirst(_('reports|model|report_route|report_type')),
    )
    unit = models.ForeignKey(
        to=Unit,
        on_delete=models.CASCADE,
        verbose_name=capfirst(_('reports|model|report_route|unit')),
    )
    telegram_chat = models.ForeignKey(
        to=TelegramChat,
        on_delete=models.CASCADE,
        verbose_name=_('reports|model|report_route|telegram chat'),
    )

    class Meta:
        verbose_name = _('reports|model|report_route')
        verbose_name_plural = _('reports|model|report_routes')
        unique_together = ('report_type', 'unit', 'telegram_chat')
