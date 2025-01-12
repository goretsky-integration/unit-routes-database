from rest_framework import serializers

__all__ = (
    'AccountNameSerializer',
    'AccountTokensRetrieveOutputSerializer',
    'AccountCookiesRetrieveOutputSerializer',
)


class AccountNameSerializer(serializers.Serializer):
    account_name = serializers.CharField(min_length=2, max_length=64)


class AccountTokensRetrieveOutputSerializer(serializers.Serializer):
    account_name = serializers.CharField(min_length=2, max_length=64)
    access_token = serializers.CharField(min_length=1, max_length=255)
    refresh_token = serializers.CharField(min_length=1, max_length=255)


class AccountCookiesRetrieveOutputSerializer(serializers.Serializer):
    account_name = serializers.CharField(min_length=2, max_length=64)
    cookies = serializers.DictField()
