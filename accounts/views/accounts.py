from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.selectors import get_accounts

__all__ = ('AccountListApi',)


class AccountListApi(APIView):

    def get(self, request: Request) -> Response:
        accounts = get_accounts()
        return Response(accounts)
