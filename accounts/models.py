from django.db import models

from django.utils.text import gettext_lazy as _


class AccountRole(models.Model):
    id = models.PositiveSmallIntegerField(
        primary_key=True,
        verbose_name=_('accounts|model|account_role|id')
    )
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('accounts|model|account_role|name'),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('accounts|model|account_role')
        verbose_name_plural = _('accounts|model|account_roles')


class Account(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('accounts|model|account|name'),
    )
    roles = models.ManyToManyField(
        to=AccountRole,
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
