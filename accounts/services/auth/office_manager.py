from dataclasses import dataclass
from dataclasses import dataclass
from enum import IntEnum
from typing import Protocol
from uuid import UUID

import httpx
from bs4 import BeautifulSoup
from django.conf import settings

from accounts.models import Account
from accounts.selectors import get_office_manager_accounts
from accounts.services.accounts import (
    AccountWithPlainCredentials,
    decrypt_account,
)
from accounts.services.crypt import encrypt_dict
from units.models import Unit


@dataclass(frozen=True, slots=True)
class AccountLoginConfig:
    country_code: str
    remember_login: bool


@dataclass(frozen=True, slots=True)
class EmptyAccountLoginFormData:
    return_url: str
    request_verification_token: str


@dataclass(frozen=True, slots=True)
class FilledAccountLoginFormData(EmptyAccountLoginFormData):
    username: str
    password: str
    tenant_name: str
    country_code: str
    auth_method: str
    remember_login: bool


@dataclass(frozen=True, slots=True)
class ConnectAuthorizeFormData:
    client_id: str
    redirect_uri: str
    response_type: str
    scope: str
    code_challenge: str
    code_challenge_method: str
    response_mode: str
    nonce: str
    state: str


class RoleId(IntEnum):
    SHIFT_MANAGER = 3
    OFFICE_MANAGER = 7
    ACCOUNTANT = 16


@dataclass(frozen=True, slots=True)
class SelectDepartmentFormData:
    request_verification_token: str


@dataclass(frozen=True, slots=True)
class SelectRoleFormData:
    request_verification_token: str


@dataclass(frozen=True, slots=True)
class SignInOidcFormData:
    code: str
    scope: str
    state: str
    session_state: str


class IAccountLoginConfig(Protocol):
    country_code: str
    remember_login: bool


def parse_account_login_form_data(
        account_login_form_html: str,
) -> EmptyAccountLoginFormData:
    soup = BeautifulSoup(account_login_form_html, 'lxml')

    return_url = soup.find(
        attrs={'name': 'ReturnUrl'},
    )['value']
    request_verification_token = soup.find(
        attrs={'name': '__RequestVerificationToken'},
    )['value']

    return EmptyAccountLoginFormData(
        return_url=return_url,
        request_verification_token=request_verification_token,
    )


def fill_account_login_form_data(
        *,
        empty_account_login_form_data: EmptyAccountLoginFormData,
        office_manager_account: AccountWithPlainCredentials,
        country_code: str,
) -> FilledAccountLoginFormData:
    return FilledAccountLoginFormData(
        return_url=empty_account_login_form_data.return_url,
        request_verification_token=empty_account_login_form_data
        .request_verification_token,

        country_code=country_code,
        remember_login=True,

        username=office_manager_account.login,
        password=office_manager_account.password,

        tenant_name='dodopizza',
        auth_method='local',
    )


def parse_connect_authorize_form_data(
        connect_authorize_form_html: str,
) -> ConnectAuthorizeFormData:
    required_credentials_names = (
        'client_id',
        'redirect_uri',
        'response_type',
        'scope',
        'code_challenge',
        'code_challenge_method',
        'response_mode',
        'nonce',
        'state',
    )

    soup = BeautifulSoup(connect_authorize_form_html, 'lxml')

    tags_with_credentials = soup.find_all(
        attrs={'name': required_credentials_names},
    )
    connect_authorize_form_data = {
        tag['name']: tag['value']
        for tag in tags_with_credentials
    }
    return ConnectAuthorizeFormData(**connect_authorize_form_data)


def parse_select_department_form(
        select_department_form_html: str,
) -> SelectDepartmentFormData:
    soup = BeautifulSoup(select_department_form_html, 'lxml')

    request_verification_token = soup.find(
        attrs={'name': '__RequestVerificationToken'},
    )['value']

    return SelectDepartmentFormData(
        request_verification_token=request_verification_token,
    )


def parse_select_role_form(
        select_role_form_html: str,
) -> SelectRoleFormData:
    soup = BeautifulSoup(select_role_form_html, 'lxml')

    request_verification_token = soup.find(
        attrs={'name': '__RequestVerificationToken'},
    )['value']

    return SelectRoleFormData(
        request_verification_token=request_verification_token,
    )


def parse_sign_in_oidc_form_data(
        sign_in_oidc_form_html: str,
) -> SignInOidcFormData:
    required_credentials_names = ('code', 'scope', 'state', 'session_state')

    soup = BeautifulSoup(sign_in_oidc_form_html, 'lxml')

    tags_with_credentials = soup.find_all(
        attrs={'name': required_credentials_names},
    )
    sign_in_oidc_form_data = {
        tag['name']: tag['value']
        for tag in tags_with_credentials
    }
    return SignInOidcFormData(**sign_in_oidc_form_data)


class OfficeManagerService:

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

    def go_to_office_manager_domain(self) -> str:
        response = self._http_client.get('/')
        return str(response.text)

    def send_sign_in_oidc_form_data(
            self,
            sign_in_oidc_form_data: SignInOidcFormData,
    ) -> str:
        request_data = {
            'code': sign_in_oidc_form_data.code,
            'scope': sign_in_oidc_form_data.scope,
            'state': sign_in_oidc_form_data.state,
            'session_state': sign_in_oidc_form_data.session_state,
        }
        url = '/signin-oidc'
        response = self._http_client.post(
            url=url,
            data=request_data,
        )
        return str(response.text)

    def send_select_role_form_data(
            self,
            *,
            select_role_form_data: SelectRoleFormData,
            selected_role_id: int | None = None,
    ) -> str:
        request_data = {
            'roleId': selected_role_id,
            '__RequestVerificationToken':
                select_role_form_data.request_verification_token,
        }
        url = '/Infrastructure/Authenticate/SelectRole'
        response = self._http_client.post(url, data=request_data)
        return str(response.text)

    def send_select_department_form_data(
            self,
            *,
            select_department_form_data: SelectDepartmentFormData,
            selected_department_uuid: UUID | None = None,
    ) -> str:
        request_data = {
            'uuid': selected_department_uuid,
            '__RequestVerificationToken':
                select_department_form_data.request_verification_token,
        }
        url = '/Infrastructure/Authenticate/SelectDepartment'
        response = self._http_client.post(url, data=request_data)
        return str(response.text)


class DodoISAuthService:

    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client

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
            'Username': account_login_form_data.username,
            'Password': account_login_form_data.password,
            'TenantName': account_login_form_data.tenant_name,
            'CountryCode': account_login_form_data.country_code,
            'authMethod': account_login_form_data.auth_method,
            '__RequestVerificationToken':
                account_login_form_data.request_verification_token,
            'RememberLogin': account_login_form_data.remember_login,
        }
        url = '/account/login'
        response = self._http_client.post(
            url=url,
            data=request_data,
        )
        return response.text


class OfficeManagerAccountAuthenticator:

    def __init__(
            self,
            office_manager_service: OfficeManagerService,
            dodo_is_auth_service: DodoISAuthService,
            account: AccountWithPlainCredentials,
            country_code: str,
    ):
        self.__office_manager_service = office_manager_service
        self.__dodo_is_auth_service = dodo_is_auth_service
        self.__account = account
        self.__country_code = country_code

    def basic_authenticate(self) -> str:
        connect_authorize_form_html = (
            self.__office_manager_service.go_to_office_manager_domain())
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
            sign_in_oidc_form_html=sign_in_oidc_form_html
        )
        return self.__office_manager_service.send_sign_in_oidc_form_data(
            sign_in_oidc_form_data=sign_in_oidc_form_data
        )

    def authenticate_in_specific_department(self, department_uuid: UUID):
        select_department_form_html = self.basic_authenticate()
        select_department_form_data = parse_select_department_form(
            select_department_form_html=select_department_form_html,
        )
        self.__office_manager_service.send_select_department_form_data(
            select_department_form_data=select_department_form_data,
            selected_department_uuid=department_uuid,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class OfficeManagerAccountCookiesRefreshInteractor:
    account: Account
    department_uuid: UUID

    def execute(self):
        account_with_plain_credentials = decrypt_account(self.account)

        office_manager_base_url = (
            f'https://officemanager.dodopizza.'
            f'{settings.LANGUAGE_CODE}'
        )
        auth_base_url = 'https://auth.dodois.io'

        with (
            httpx.Client(base_url=auth_base_url) as auth_http_client,
            httpx.Client(base_url=office_manager_base_url)
            as office_manager_http_client,
        ):
            dodo_is_auth_service = DodoISAuthService(auth_http_client)
            office_manager_service = OfficeManagerService(
                office_manager_http_client
            )
            account_authenticator = OfficeManagerAccountAuthenticator(
                office_manager_service=office_manager_service,
                dodo_is_auth_service=dodo_is_auth_service,
                account=account_with_plain_credentials,
                country_code=settings.LANGUAGE_CODE,
            )
            account_authenticator.authenticate_in_specific_department(
                department_uuid=self.department_uuid,
            )
            cookies = dict(office_manager_http_client.cookies)

        self.account.encrypted_cookies = encrypt_dict(cookies)
        self.account.save()
