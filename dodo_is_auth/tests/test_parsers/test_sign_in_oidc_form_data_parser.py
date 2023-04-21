from dodo_is_auth.models import SignInOidcFormData, HTML
from dodo_is_auth.parsers import parse_sign_in_oidc_form_data


def test_parse_sign_in_oidc_form_data():
    sign_in_oidc_form_html = '''
        <form>
            <input type="hidden" name="code" value="12345">
            <input type="hidden" name="scope" value="email">
            <input type="hidden" name="state" value="xyz">
            <input type="hidden" name="session_state" value="abc">
        </form>
    '''
    # Expected output
    expected_output = SignInOidcFormData(
        code='12345',
        scope='email',
        state='xyz',
        session_state='abc',
    )

    # Call the function
    result = parse_sign_in_oidc_form_data(HTML(sign_in_oidc_form_html))

    # Check the result
    assert result == expected_output
