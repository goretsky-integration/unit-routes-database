from django.db import models
from django.utils.translation import gettext_lazy as _

from django.utils.text import capfirst


class ReportType(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name=_('reports|model|report_type|name'),
    )
    verbose_name = models.CharField(
        max_length=64,
        verbose_name=_('reports|model|report_type|verbose_name'),
    )
    parent = models.ForeignKey(
        to='ReportType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('reports|model|report_type|parent'),
    )
    priority = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('reports|model|report_type|priority'),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=capfirst(_('reports|model|report_type|is_active')),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('reports|model|report_type')
        verbose_name_plural = _('reports|model|report_types')
