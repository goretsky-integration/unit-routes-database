import httpx

from accounts.services.auth.common_models import (
    ConnectAuthorizeFormData,
    FilledAccountLoginFormData,
)


class DodoISAuthService:

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    @property
    def cookies(self) -> dict[str, str]:
        return dict(self._http_client.cookies)

    def send_connect_authorize_form_data(
            self,
            connect_authorize_form_data: ConnectAuthorizeFormData,
    ) -> str:
        request_data = {
            'client_id': connect_authorize_form_data.client_id,
            'redirect_uri': connect_authorize_form_data.redirect_uri,
            'response_type': connect_authorize_form_data.response_type,
            'scope': connect_authorize_form_data.scope,
            'code_challenge': connect_authorize_form_data.code_challenge,
            'code_challenge_method':
                connect_authorize_form_data.code_challenge_method,
            'response_mode': connect_authorize_form_data.response_mode,
            'nonce': connect_authorize_form_data.nonce,
            'state': connect_authorize_form_data.state,
        }
        url = '/connect/authorize'
        response = self._http_client.post(url, data=request_data)
        return str(response.text)

    def send_account_login_form_data(
            self,
            *,
            account_login_form_data: FilledAccountLoginFormData,
    ) -> str:
        request_data = {
            'ReturnUrl': account_login_form_data.return_url,
            'Login': account_login_form_data.username,
            'Password': account_login_form_data.password,
            'authMethod': account_login_form_data.auth_method,
            '__RequestVerificationToken':
                account_login_form_data.request_verification_token,
            'RememberLogin': account_login_form_data.remember_login,
        }
        url = '/login/password'
        response = self._http_client.post(
            url=url,
            data=request_data,
        )
        return response.text
