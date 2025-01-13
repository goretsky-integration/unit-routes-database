from accounts.models import Account, AccountCookies
from accounts.services.crypt import encrypt_dict


__all__ = ('update_account_cookies',)


def update_account_cookies(account: Account, cookies: dict) -> None:
    AccountCookies.objects.update_or_create(
        account=account,
        defaults={'encrypted_cookies': encrypt_dict(cookies)},
    )
