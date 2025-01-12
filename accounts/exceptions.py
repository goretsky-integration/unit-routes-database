from rest_framework.exceptions import APIException
from rest_framework import status

__all__ = ('AccountNotFoundError', 'AccountTokensNotFoundError')


class AccountNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'account_not_found'
    default_detail = 'Account not found'


class AccountTokensNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'account_tokens_not_found'
    default_detail = 'Account tokens not found'
