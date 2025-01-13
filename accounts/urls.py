from django.urls import path

from accounts.views import (
    AccountCookiesRetrieveApi, AccountListApi, AccountTokensRetrieveApi,
)

urlpatterns = [
    path(
        r'accounts/',
        AccountListApi.as_view(),
        name='account-list',
    ),
    path(
        r'auth/token/',
        AccountTokensRetrieveApi.as_view(),
        name='account-token-retrieve-update',
    ),
    path(
        r'auth/cookies/',
        AccountCookiesRetrieveApi.as_view(),
        name='account-cookies-retrieve-update',
    ),
]
