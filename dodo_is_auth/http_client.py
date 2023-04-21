import contextlib

import httpx

from dodo_is_auth.models import HTTPClient


@contextlib.contextmanager
def closing_dodo_is_auth_http_client(
        *,
        base_url: str,
        timeout: int | float = 15,
) -> HTTPClient:
    if not base_url:
        raise ValueError('Base url is not provided')

    headers = {'User-Agent': 'dodoextbot'}
    with httpx.Client(
            base_url=base_url,
            headers=headers,
            follow_redirects=True,
            timeout=timeout,
    ) as client:
        yield HTTPClient(client)
