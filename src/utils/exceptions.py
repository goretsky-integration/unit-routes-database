"""
- NoCookiesError
- NoTokenError
- DatabaseConnectionError
"""

from fastapi import status
from fastapi.exceptions import HTTPException


class NoCookiesError(HTTPException):

    def __init__(self, account_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No cookies by account name "{account_name}"',
        )


class NoTokenError(HTTPException):

    def __init__(self, account_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No access token by account name "{account_name}"',
        )


class DatabaseConnectionError(HTTPException):

    def __init__(self, text: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=text,
        )
