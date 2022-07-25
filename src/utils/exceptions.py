"""
- NotFoundError
    - NoCookiesError
    - NoTokenError
    - NoReportError
- DatabaseConnectionError
"""

from fastapi import status
from fastapi.exceptions import HTTPException


class NotFoundError(HTTPException):
    detail = 'Not found'

    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=self.detail)


class NoReportError(NotFoundError):
    detail = 'Report by this report type and chat id did not found'


class NoCookiesError(NotFoundError):
    detail = 'Cookies did not found'


class NoTokenError(NotFoundError):
    detail = 'Token did not found'


class DatabaseConnectionError(HTTPException):

    def __init__(self, text: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=text,
        )
