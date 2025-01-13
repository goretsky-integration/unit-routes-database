from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import (
    AccountCookiesRetrieveOutputSerializer,
    AccountNameSerializer,
)
from accounts.services.accounts import get_decrypted_account_cookies

__all__ = ('AccountCookiesRetrieveApi',)


class AccountCookiesRetrieveApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = AccountNameSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        account_name: str = serializer.validated_data['account_name']
        account_cookies = get_decrypted_account_cookies(account_name)
        serializer = AccountCookiesRetrieveOutputSerializer(account_cookies)
        return Response(serializer.data)
