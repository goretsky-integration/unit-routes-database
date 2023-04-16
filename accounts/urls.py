from django.urls import path

from accounts.views import (
    AccountListApi,
    DodoISAPICredentialsRetrieveApi,
    DodoISSessionCredentialsRetrieveApi,
)

urlpatterns = [
    path('accounts/', AccountListApi.as_view()),
    path('auth/token/', DodoISAPICredentialsRetrieveApi.as_view()),
    path('auth/cookies/', DodoISSessionCredentialsRetrieveApi.as_view()),
]
