from django.db import models
from django.utils.text import gettext_lazy as _

from units.models import Department, Unit


class Account(models.Model):
    class Role(models.IntegerChoices):
        SHIFT_MANAGER = 3, _('accounts|model|account|role|shift_manager')
        OFFICE_MANAGER = 7, _('accounts|model|account|role|office_manager')

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('accounts|model|account|name'),
    )
    role = models.PositiveSmallIntegerField(
        null=True,
        choices=Role.choices,
        verbose_name=_('accounts|model|account|role'),
    )
    login = models.CharField(
        max_length=255,
        verbose_name=_('accounts|model|account|login'),
    )
    password = models.CharField(
        max_length=255,
        verbose_name=_('accounts|model|account|password'),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('accounts|model|account')
        verbose_name_plural = _('accounts|model|accounts')

    @property
    def role_name(self) -> str:
        return self.Role(self.role).name


class DodoISAPICredentials(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    department = models.ForeignKey(
        to=Department,
        on_delete=models.CASCADE,
        null=True,
    )
    updated_at = models.DateTimeField(auto_now=True)


class OfficeManagerSessionCredentials(models.Model):
    account = models.ForeignKey(
        to=Account,
        on_delete=models.CASCADE,
    )
    cookies = models.JSONField(null=True)
    department = models.ForeignKey(
        to=Department,
        on_delete=models.CASCADE,
    )
    updated_at = models.DateTimeField(auto_now=True)


class ShiftManagerSessionCredentials(models.Model):
    account = models.ForeignKey(
        to=Account,
        on_delete=models.CASCADE,
    )
    cookies = models.JSONField(null=True)
    unit = models.ForeignKey(
        to=Unit,
        on_delete=models.CASCADE,
    )
    updated_at = models.DateTimeField(auto_now=True)
