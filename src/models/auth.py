from pydantic import BaseModel

__all__ = (
    'Token',
    'AuthCookies',
)


class Token(BaseModel):
    account_name: str
    access_token: str
    refresh_token: str


class AuthCookies(BaseModel):
    account_name: str
    cookies: dict[str, str]
