from dodo_is_auth.models import (
    AccountLoginConfig,
    EmptyAccountLoginFormData,
    OfficeManagerAccount,
)
from dodo_is_auth.parsers import fill_account_login_form_data


def test_fill_account_login_form_data():
    empty_form_data = EmptyAccountLoginFormData(
        return_url='https://example.com/login',
        request_verification_token='abcd1234',
    )
    login_config = AccountLoginConfig(
        country_code='US',
        remember_login=True,
    )
    account = OfficeManagerAccount(
        name='John Smith',
        login='johnsmith',
        password='password123',
    )

    filled_form_data = fill_account_login_form_data(
        empty_account_login_form_data=empty_form_data,
        account_login_config=login_config,
        office_manager_account=account,
    )

    assert filled_form_data.return_url == empty_form_data.return_url
    assert filled_form_data.request_verification_token == empty_form_data.request_verification_token
    assert filled_form_data.country_code == login_config.country_code
    assert filled_form_data.remember_login == login_config.remember_login
    assert filled_form_data.username == account.login
    assert filled_form_data.password == account.password
    assert filled_form_data.tenant_name == 'dodopizza'
    assert filled_form_data.auth_method == 'local'
