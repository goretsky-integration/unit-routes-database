import pytest
import httpx
from dodo_is_auth.models import (
    HTTPClient,
    ConnectAuthorizeFormData,
    HTML,
    FilledAccountLoginFormData,
)
from dodo_is_auth.auth import DodoISAuthService


@pytest.fixture
def http_client():
    return HTTPClient(httpx.Client(base_url='https://example.com'))


@pytest.fixture
def dodo_is_auth_service(http_client):
    return DodoISAuthService(http_client)


def test_send_connect_authorize_form_data(httpx_mock, dodo_is_auth_service):
    expected_html = HTML('<html><body>Authorization form</body></html>')
    httpx_mock.add_response(text=expected_html)
    connect_authorize_form_data = ConnectAuthorizeFormData(
        client_id='client_id',
        redirect_uri='https://example.com/callback',
        response_type='code',
        scope='openid profile email',
        code_challenge='code_challenge',
        code_challenge_method='S256',
        response_mode='form_post',
        nonce='nonce',
        state='state',
    )

    html = dodo_is_auth_service.send_connect_authorize_form_data(
        connect_authorize_form_data=connect_authorize_form_data,
    )
    assert html == expected_html


def test_send_account_login_form_data(httpx_mock, dodo_is_auth_service):
    expected_html = HTML('<html><body>Logged in successfully</body></html>')
    httpx_mock.add_response(text=expected_html)
    filled_account_login_form_data = FilledAccountLoginFormData(
        return_url='https://example.com',
        username='username',
        password='password',
        tenant_name='tenant_name',
        country_code='+1',
        auth_method='pwd',
        request_verification_token='token',
        remember_login=True,
    )

    html = dodo_is_auth_service.send_account_login_form_data(
        account_login_form_data=filled_account_login_form_data,
    )
    assert html == expected_html
