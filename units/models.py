from django.db import models
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


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


class Region(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('units|model|region|name'),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('units|model|region')
        verbose_name_plural = _('units|model|regions')


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
    office_manager_account_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    dodo_is_api_account_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    shift_manager_account_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    region = models.ForeignKey(
        to=Region,
        on_delete=models.CASCADE,
        verbose_name=capfirst(_('units|model|unit|region')),
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
