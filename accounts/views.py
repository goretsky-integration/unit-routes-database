from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.models import (
    Account,
    DodoISAPICredentials,
    DodoISSessionCredentials
)
from core.exceptions import NotFoundError
from core.serializers import LimitOffsetSerializer


class AccountListApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        role = serializers.CharField(source='role_name')

        class Meta:
            model = Account
            fields = ('name', 'login', 'password', 'role')

    def get(self, request: Request):
        serializer = LimitOffsetSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

        accounts = (
            Account.objects.all()[offset:limit + offset + 1]
            .only('name', 'login', 'password', 'role')
        )
        is_end_of_list_reached = len(accounts) < limit + 1

        output_serializer = self.OutputSerializer(accounts[:limit], many=True)
        response_data = {
            'accounts': output_serializer.data,
            'is_end_of_list_reached': is_end_of_list_reached,
        }
        return Response(response_data)


class DodoISAPICredentialsRetrieveApi(APIView):

    class InputUpdateSerializer(serializers.Serializer):
        account_name = serializers.CharField(min_length=1, max_length=255)
        access_token = serializers.CharField(min_length=1, max_length=255)
        refresh_token = serializers.CharField(min_length=1, max_length=255)

    class InputRetrieveSerializer(serializers.Serializer):
        account_name = serializers.CharField(min_length=1, max_length=255)

    class OutputSerializer(serializers.ModelSerializer):
        account_name = serializers.CharField(source='account.name')

        class Meta:
            model = DodoISAPICredentials
            fields = ('account_name', 'access_token', 'refresh_token')

    def get(self, request: Request):
        serializer = self.InputRetrieveSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        account_name: str = serialized_data['account_name']
        dodo_is_api_credentials = (
            DodoISAPICredentials.objects
            .select_related('account')
            .filter(account__name=account_name)
            .only('access_token', 'account__name', 'refresh_token')
            .first()
        )
        if dodo_is_api_credentials is None:
            raise NotFoundError('No API tokens')
        return Response(self.OutputSerializer(dodo_is_api_credentials).data)

    def patch(self, request: Request):
        serializer = self.InputUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        account_name: str = serialized_data['account_name']
        access_token: str = serialized_data['access_token']
        refresh_token: str = serialized_data['refresh_token']

        updated_rows_count = (
            DodoISAPICredentials.objects
            .select_related('account')
            .filter(account__name=account_name)
            .update(access_token=access_token, refresh_token=refresh_token)
        )
        response_status = (status.HTTP_204_NO_CONTENT if updated_rows_count
                           else status.HTTP_404_NOT_FOUND)
        return Response(status=response_status)


class DodoISSessionCredentialsRetrieveApi(APIView):

    class InputRetrieveSerializer(serializers.Serializer):
        account_name = serializers.CharField(min_length=1, max_length=255)

    class InputUpdateSerializer(serializers.Serializer):
        account_name = serializers.CharField(min_length=1, max_length=255)
        cookies = serializers.JSONField()

    class OutputSerializer(serializers.ModelSerializer):
        account_name = serializers.CharField(source='account.name')

        class Meta:
            model = DodoISSessionCredentials
            fields = ('account_name', 'cookies')

    def get(self, request: Request):
        serializer = self.InputRetrieveSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        account_name: str = serialized_data['account_name']
        dodo_is_session_credentials = (
            DodoISSessionCredentials.objects
            .select_related('account')
            .filter(account__name=account_name)
            .only('account__name', 'cookies')
            .first()
        )
        if dodo_is_session_credentials is None:
            raise NotFoundError('No cookies')
        return Response(self.OutputSerializer(dodo_is_session_credentials).data)

    def patch(self, request: Request):
        serializer = self.InputUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        account_name: str = serialized_data['account_name']
        cookies = serialized_data['cookies']

        updated_rows_count = (
            DodoISSessionCredentials.objects
            .select_related('account')
            .filter(account__name=account_name)
            .update(cookies=cookies)
        )
        response_status = (status.HTTP_204_NO_CONTENT if updated_rows_count
                           else status.HTTP_404_NOT_FOUND)
        return Response(status=response_status)
