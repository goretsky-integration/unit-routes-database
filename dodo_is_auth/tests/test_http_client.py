import httpx
import pytest
from pytest_httpx import HTTPXMock

from dodo_is_auth.http_client import closing_dodo_is_auth_http_client
from dodo_is_auth.models import HTTPClient


def test_closing_dodo_is_auth_http_client_with_base_url():
    base_url = "https://example.com"
    with closing_dodo_is_auth_http_client(base_url=base_url) as auth_client:
        assert isinstance(auth_client, httpx.Client)


def test_closing_dodo_is_auth_http_client_with_missing_base_url():
    with pytest.raises(ValueError, match="Base url is not provided"):
        with closing_dodo_is_auth_http_client(base_url=''):
            pass


def test_closing_dodo_is_auth_http_client_with_timeout(httpx_mock: HTTPXMock):
    base_url = "https://example.com"
    timeout = 10
    with closing_dodo_is_auth_http_client(
            base_url=base_url,
            timeout=timeout
    ) as auth_client:
        assert auth_client.timeout == httpx.Timeout(timeout)
