from django.urls import path

from accounts.views import AccountsListView


urlpatterns = [
    path('accounts/', AccountsListView.as_view()),
]
