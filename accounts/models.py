from django.db import models

__all__ = ('Account', 'AccountCookies', 'AccountTokens')


class Account(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    encrypted_login = models.CharField(max_length=255)
    encrypted_password = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AccountTokens(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    encrypted_access_token = models.CharField(max_length=255)
    encrypted_refresh_token = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account.name

    class Meta:
        verbose_name_plural = 'accounts tokens'


class AccountCookies(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    encrypted_cookies = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account.name

    class Meta:
        verbose_name_plural = 'accounts cookies'
