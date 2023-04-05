from django.db import models
from django.utils.translation import gettext_lazy as _

from reports.models.report_types import ReportType
from units.models import Unit


class UserRole(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name=_('user_roles|model|user_role|name'),
    )
    access_code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name=_('user_roles|model|user_role|access_code'),
    )
    report_types = models.ManyToManyField(
        to=ReportType,
        verbose_name=_('user_roles|model|user_role|report_types'),
    )
    units = models.ManyToManyField(
        to=Unit,
        verbose_name=_('user_roles|model|user_role|units'),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('user_roles|model|user_role')
        verbose_name_plural = _('user_roles|model|user_roles')
