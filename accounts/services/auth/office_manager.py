from dataclasses import dataclass
from uuid import UUID

import httpx
from bs4 import BeautifulSoup
from django.conf import settings

from accounts.models import AccountCookies
from accounts.services.accounts import (
    AccountWithPlainCredentials,
    decrypt_account,
)
from accounts.services.auth.common_models import (
    ConnectAuthorizeFormData, EmptyAccountLoginFormData,
    FilledAccountLoginFormData, SelectDepartmentFormData, SelectRoleFormData,
    SignInOidcFormData,
)
from accounts.services.auth.dodo_is_auth import DodoISAuthService
from accounts.services.crypt import encrypt_dict


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
        scope: str,
) -> SignInOidcFormData:
    required_credentials_names = ('code', 'state', 'session_state')

    soup = BeautifulSoup(sign_in_oidc_form_html, 'lxml')

    tags_with_credentials = soup.find_all(
        attrs={'name': required_credentials_names},
    )
    sign_in_oidc_form_data = {
        tag['name']: tag['value']
        for tag in tags_with_credentials
    }
    return SignInOidcFormData(**sign_in_oidc_form_data, scope=scope)


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
    account_cookies: AccountCookies
    department_uuid: UUID

    def execute(self):
        account_with_plain_credentials = decrypt_account(
            self.account_cookies.account,
        )

        office_manager_base_url = (
            f'https://officemanager.dodopizza.'
            f'{settings.LANGUAGE_CODE}'
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
            ) as office_manager_http_client,
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

        self.account_cookies.encrypted_cookies = encrypt_dict(cookies)
        self.account_cookies.save()
