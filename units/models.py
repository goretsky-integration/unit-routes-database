from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Account


class Department(models.Model):
    id = models.PositiveSmallIntegerField(
        primary_key=True,
        verbose_name=_('units|model|department|id'),
    )
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('units|model|department|name'),
    )
    uuid = models.UUIDField(
        unique=True,
        verbose_name=_('units|model|department|uuid'),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('units|model|department')
        verbose_name_plural = _('units|model|departments')


class Unit(models.Model):
    id = models.IntegerField(
        primary_key=True,
        verbose_name=_('units|model|unit|id'),
    )
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('units|model|unit|name'),
    )
    uuid = models.UUIDField(
        unique=True,
        verbose_name=_('units|model|unit|uuid'),
    )
    department = models.ForeignKey(
        to=Department,
        on_delete=models.CASCADE,
        verbose_name=_('units|model|unit|department'),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('units|model|unit')
        verbose_name_plural = _('units|model|units')
