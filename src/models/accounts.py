from pydantic import BaseModel

__all__ = (
    'Account',
)


class Account(BaseModel):
    login: str
    password: str
    name: str
