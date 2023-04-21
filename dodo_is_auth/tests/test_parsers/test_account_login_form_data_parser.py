import pytest

from dodo_is_auth.models import HTML, EmptyAccountLoginFormData
from dodo_is_auth.parsers import parse_account_login_form_data


def test_parse_account_login_form_data():
    html = HTML('''
    <form>
        <input name="ReturnUrl" value="https://example.com">
        <input name="__RequestVerificationToken" value="abcd1234">
    </form>
    ''')

    form_data = parse_account_login_form_data(html)

    assert isinstance(form_data, EmptyAccountLoginFormData)
    assert form_data.return_url == 'https://example.com'
    assert form_data.request_verification_token == 'abcd1234'


def test_parse_account_login_form_data_missing_input():
    html = HTML('<form></form>')

    with pytest.raises(TypeError):
        parse_account_login_form_data(html)
