from dataclasses import dataclass
from uuid import UUID

import httpx
from django.conf import settings

from accounts.models import AccountCookies
from accounts.services.accounts import (
    AccountWithPlainCredentials,
    decrypt_account,
)
from accounts.services.auth.common_models import SignInOidcFormData
from accounts.services.auth.dodo_is_auth import DodoISAuthService
from accounts.services.auth.office_manager import \
    (
    fill_account_login_form_data, parse_account_login_form_data,
    parse_connect_authorize_form_data, parse_sign_in_oidc_form_data,
)
from accounts.services.crypt import encrypt_dict


class ShiftManagerService:

    def __init__(
            self,
            http_client: httpx.Client,
    ):
        self.http_client = http_client

    @property
    def cookies(self) -> dict[str, str]:
        return dict(self.http_client.cookies)

    def go_to_shift_manager_domain(self) -> str:
        response = self.http_client.get(
            url='/Infrastructure/Authenticate/Oidc'
        )
        return response.text

    def send_sign_in_oidc_form_data(
            self,
            sign_in_oidc_form_data: SignInOidcFormData,
            cookies,
    ) -> str:
        request_data = {
            'code': sign_in_oidc_form_data.code,
            'scope': sign_in_oidc_form_data.scope,
            'state': sign_in_oidc_form_data.state,
            'session_state': sign_in_oidc_form_data.session_state,
        }
        response = self.http_client.post(
            url='/signin-oidc',
            data=request_data,
            cookies=cookies,
        )
        return response.text

    def send_select_role_form_data(
            self, department_uuid: UUID, cookies
    ) -> None:
        request_data = {
            'departmentId': department_uuid.hex,
            'role': 'ShiftManager',
        }
        self.http_client.post(
            url='/Infrastructure/Authenticate/SetRole',
            json=request_data,
            cookies=cookies,
        )


class ShiftManagerAccountAuthenticator:

    def __init__(
            self,
            shift_manager_service: ShiftManagerService,
            dodo_is_auth_service: DodoISAuthService,
            account: AccountWithPlainCredentials,
            country_code: str,
    ):
        self.__shift_manager_service = shift_manager_service
        self.__dodo_is_auth_service = dodo_is_auth_service
        self.__account = account
        self.__country_code = country_code

    def authenticate_specific_unit(self, unit_uuid: UUID) -> dict[str, str]:
        connect_authorize_form_html = (
            self.__shift_manager_service.go_to_shift_manager_domain())
        connect_authorize_form_data = parse_connect_authorize_form_data(
            connect_authorize_form_html=connect_authorize_form_html,
        )

        account_login_form_html = (
            self.__dodo_is_auth_service.send_connect_authorize_form_data(
                connect_authorize_form_data=connect_authorize_form_data,
            ))

        empty_account_login_form_data = parse_account_login_form_data(
            account_login_form_html=account_login_form_html,
        )
        filled_account_login_form_data = fill_account_login_form_data(
            empty_account_login_form_data=empty_account_login_form_data,
            office_manager_account=self.__account,
            country_code=self.__country_code,
        )

        sign_in_oidc_form_html = (
            self.__dodo_is_auth_service.send_account_login_form_data(
                account_login_form_data=filled_account_login_form_data,
            ))
        sign_in_oidc_form_data = parse_sign_in_oidc_form_data(
            sign_in_oidc_form_html=sign_in_oidc_form_html,
            scope=connect_authorize_form_data.scope,
        )

        self.__shift_manager_service.send_sign_in_oidc_form_data(
            sign_in_oidc_form_data,
            self.__dodo_is_auth_service.cookies)

        self.__shift_manager_service.send_select_role_form_data(
            unit_uuid,
            cookies=self.__dodo_is_auth_service.cookies,
        )
        return dict(self.__shift_manager_service.cookies)


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftManagerAccountCookiesRefreshInteractor:
    account_cookies: AccountCookies
    unit_uuid: UUID

    def execute(self):
        account_with_plain_credentials = decrypt_account(
            self.account_cookies.account,
        )

        office_manager_base_url = (
            f'https://shiftmanager.dodopizza.{settings.LANGUAGE_CODE}'
        )
        auth_base_url = 'https://auth.dodois.io'

        with (
            httpx.Client(
                base_url=auth_base_url,
                headers={'User-Agent': 'dodoextbot'},
                follow_redirects=True,
            ) as auth_http_client,
            httpx.Client(
                base_url=office_manager_base_url,
                headers={'User-Agent': 'dodoextbot'},
                follow_redirects=True,
            ) as shift_manager_http_client,
        ):
            dodo_is_auth_service = DodoISAuthService(auth_http_client)
            shift_manager_service = ShiftManagerService(
                shift_manager_http_client
            )
            account_authenticator = ShiftManagerAccountAuthenticator(
                shift_manager_service=shift_manager_service,
                dodo_is_auth_service=dodo_is_auth_service,
                account=account_with_plain_credentials,
                country_code=settings.LANGUAGE_CODE,
            )
            cookies = account_authenticator.authenticate_specific_unit(
                unit_uuid=self.unit_uuid,
            )

        self.account_cookies.encrypted_cookies = encrypt_dict(cookies)
        self.account_cookies.save()
