from pydantic import BaseModel

__all__ = (
    'Token',
)


class Token(BaseModel):
    access_token: str
