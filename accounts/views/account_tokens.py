from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import (
    AccountNameSerializer,
    AccountTokensRetrieveOutputSerializer,
)
from accounts.services.accounts import get_decrypted_account_tokens

__all__ = ('AccountTokensRetrieveApi',)


class AccountTokensRetrieveApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = AccountNameSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        account_name: str = serializer.validated_data['account_name']
        account_tokens = get_decrypted_account_tokens(account_name)
        serializer = AccountTokensRetrieveOutputSerializer(account_tokens)
        return Response(serializer.data)
