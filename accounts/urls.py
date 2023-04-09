from django.urls import path

from accounts.views import AccountsListView


urlpatterns = [
    path('', AccountsListView.as_view()),
]
