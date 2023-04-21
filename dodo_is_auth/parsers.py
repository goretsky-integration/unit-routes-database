from typing import Protocol

from bs4 import BeautifulSoup

from dodo_is_auth.models import (
    HTML,
    EmptyAccountLoginFormData,
    OfficeManagerAccount,
    FilledAccountLoginFormData,
    ConnectAuthorizeFormData,
    SelectDepartmentFormData,
    SelectRoleFormData,
    SignInOidcFormData,
)


class IAccountLoginConfig(Protocol):
    country_code: str
    remember_login: bool


def parse_account_login_form_data(
        account_login_form_html: HTML,
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
        office_manager_account: OfficeManagerAccount,
        account_login_config: IAccountLoginConfig,
) -> FilledAccountLoginFormData:
    return FilledAccountLoginFormData(
        return_url=empty_account_login_form_data.return_url,
        request_verification_token=empty_account_login_form_data.request_verification_token,

        country_code=account_login_config.country_code,
        remember_login=account_login_config.remember_login,

        username=office_manager_account.login,
        password=office_manager_account.password,

        tenant_name='dodopizza',
        auth_method='local',
    )


def parse_connect_authorize_form_data(
        connect_authorize_form_html: HTML,
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
        select_department_form_html: HTML,
) -> SelectDepartmentFormData:
    soup = BeautifulSoup(select_department_form_html, 'lxml')

    request_verification_token = soup.find(
        attrs={'name': '__RequestVerificationToken'},
    )['value']

    return SelectDepartmentFormData(
        request_verification_token=request_verification_token,
    )


def parse_select_role_form(
        select_role_form_html: HTML,
) -> SelectRoleFormData:
    soup = BeautifulSoup(select_role_form_html, 'lxml')

    request_verification_token = soup.find(
        attrs={'name': '__RequestVerificationToken'},
    )['value']

    return SelectRoleFormData(
        request_verification_token=request_verification_token,
    )


def parse_sign_in_oidc_form_data(
        sign_in_oidc_form_html: HTML,
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
