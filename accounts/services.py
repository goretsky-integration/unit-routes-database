import json
from dataclasses import dataclass

from cryptography.fernet import Fernet
from django.conf import settings

from accounts.exceptions import AccountTokensNotFoundError
from accounts.models import Account, AccountCookies, AccountTokens

__all__ = (
    'upsert_account_tokens',
    'get_decrypted_account_tokens',
    'get_decrypted_account_cookies',
    'AccountCookies',
    'AccountTokens',
)


def upsert_account_tokens(
        account: Account,
        access_token: str,
        refresh_token: str,
) -> AccountTokens:
    fernet = Fernet(settings.FERNET_KEY)
    encrypted_access_token = fernet.encrypt(access_token.encode()).decode()
    encrypted_refresh_token = fernet.encrypt(refresh_token.encode()).decode()

    account_tokens, _ = AccountTokens.objects.update_or_create(
        account=account,
        defaults={
            'encrypted_access_token': encrypted_access_token,
            'encrypted_refresh_token': encrypted_refresh_token,
        },
    )

    return account_tokens


@dataclass(frozen=True, slots=True, kw_only=True)
class AccountPlainTokens:
    account_name: str
    access_token: str
    refresh_token: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AccountPlainCookies:
    account_name: str
    cookies: dict[str, str]


def get_decrypted_account_tokens(
        account_name: str
) -> AccountPlainTokens:
    try:
        account_tokens = AccountTokens.objects.get(
            account__name=account_name,
        )
    except AccountTokens.DoesNotExist:
        raise AccountTokensNotFoundError
    fernet = Fernet(settings.FERNET_KEY)
    decrypted_access_token = fernet.decrypt(
        account_tokens.encrypted_access_token,
    ).decode()
    decrypted_refresh_token = fernet.decrypt(
        account_tokens.encrypted_refresh_token
    ).decode()
    return AccountPlainTokens(
        account_name=account_name,
        access_token=decrypted_access_token,
        refresh_token=decrypted_refresh_token,
    )


def get_decrypted_account_cookies(
        account_name: str,
) -> AccountPlainCookies:
    account_cookies = AccountCookies.objects.get(
        account__name=account_name,
    )
    fernet = Fernet(settings.FERNET_KEY)
    decrypted_cookies_json = fernet.decrypt(account_cookies.encrypted_cookies)
    decrypted_cookies = json.loads(decrypted_cookies_json)
    return AccountPlainCookies(
        account_name=account_name,
        cookies=decrypted_cookies,
    )
