from django.db import models

from django.utils.text import gettext_lazy as _


class Account(models.Model):
    class Role(models.IntegerChoices):
        SHIFT_MANAGER = 3, _('accounts|model|account|role|shift_manager')
        OFFICE_MANAGER = 7, _('accounts|model|account|role|office_manager')

    name = models.CharField(max_length=255, unique=True)
    role = models.PositiveSmallIntegerField(choices=Role.choices)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class DodoISAPICredentials(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)


class DodoISSessionCredentials(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    cookies = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
