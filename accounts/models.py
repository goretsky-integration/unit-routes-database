from django.db import models

from django.utils.text import gettext_lazy as _


class Account(models.Model):
    class AccountRole(models.IntegerChoices):
        SHIFT_MANAGER = 3, _('accounts|model|account|role|shift_manager')
        OFFICE_MANAGER = 7, _('accounts|model|account|role|office_manager')

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('accounts|model|account|name'),
    )
    role = models.PositiveSmallIntegerField(
        null=True,
        choices=AccountRole.choices,
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


class DodoISAPICredentials(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)


class DodoISSessionCredentials(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    cookies = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
