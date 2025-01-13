from dataclasses import dataclass

import httpx
from django.conf import settings

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string, encrypt_string


@dataclass(frozen=True, slots=True, kw_only=True)
class APITokensRefreshInteractor:
    account_tokens: AccountTokens

    def execute(self) -> None:
        refresh_token = decrypt_string(
            self.account_tokens.encrypted_refresh_token,
        )

        url = 'https://auth.dodois.io/connect/token'
        request_data = {
            'client_id': settings.DODO_IS_API_CLIENT_ID,
            'client_secret': settings.DODO_IS_API_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        with httpx.Client() as http_client:
            response = http_client.post(url, data=request_data)

        response_data = response.json()

        plain_access_token: str = response_data['access_token']
        plain_refresh_token: str = response_data['refresh_token']

        self.account_tokens.encrypted_access_token = encrypt_string(
            plain_access_token,
        )
        self.account_tokens.encrypted_refresh_token = encrypt_string(
            plain_refresh_token,
        )
        self.account_tokens.save()
