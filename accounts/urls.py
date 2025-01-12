from django.urls import path

from accounts.views import AccountListApi, AccountTokensRetrieveApi

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
]
