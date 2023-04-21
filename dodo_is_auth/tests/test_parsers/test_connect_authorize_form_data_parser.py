import pytest
from bs4 import BeautifulSoup
from dodo_is_auth.models import HTML, ConnectAuthorizeFormData
from dodo_is_auth.parsers import parse_connect_authorize_form_data


@pytest.fixture
def connect_authorize_form_html() -> HTML:
    html = """
    <form>
        <input type="hidden" name="client_id" value="abc123">
        <input type="hidden" name="redirect_uri" value="http://localhost:8000/callback">
        <input type="hidden" name="response_type" value="code">
        <input type="hidden" name="scope" value="openid profile email">
        <input type="hidden" name="code_challenge" value="1234567890">
        <input type="hidden" name="code_challenge_method" value="S256">
        <input type="hidden" name="response_mode" value="form_post">
        <input type="hidden" name="nonce" value="abc123">
        <input type="hidden" name="state" value="def456">
    </form>
    """
    return HTML(html)


def test_parse_connect_authorize_form_data(connect_authorize_form_html):
    expected_data = ConnectAuthorizeFormData(
        client_id="abc123",
        redirect_uri="http://localhost:8000/callback",
        response_type="code",
        scope="openid profile email",
        code_challenge="1234567890",
        code_challenge_method="S256",
        response_mode="form_post",
        nonce="abc123",
        state="def456",
    )
    actual_data = parse_connect_authorize_form_data(connect_authorize_form_html)
    assert actual_data == expected_data


def test_parse_connect_authorize_form_data_with_missing_tag(
        connect_authorize_form_html):
    # Remove one of the input tags to simulate a missing tag
    soup = BeautifulSoup(connect_authorize_form_html, "lxml")
    input_tag = soup.find("input", attrs={"name": "client_id"})
    input_tag.extract()

    with pytest.raises(TypeError):
        parse_connect_authorize_form_data(HTML(str(soup)))
