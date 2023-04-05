from django.db import models
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


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
        max_length=64,
        verbose_name=_('units|model|unit|office_manager_account_name'),
    )
    dodo_is_api_account_name = models.CharField(
        max_length=64,
        verbose_name=_('units|model|unit|dodo_is_api_account_name'),
    )
    region = models.ForeignKey(
        to=Region,
        on_delete=models.CASCADE,
        verbose_name=capfirst(_('units|model|unit|region')),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('units|model|unit')
        verbose_name_plural = _('units|model|units')
