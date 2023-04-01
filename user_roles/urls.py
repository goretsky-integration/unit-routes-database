from django.urls import path, include

from user_roles.views import (
    UserRoleUnitsListApi,
    UserRoleRegionsListApi,
    UserRoleReportTypesListApi,
    SetUserRoleApi,
)

user_roles_urlpatterns = [
    path('regions/', UserRoleRegionsListApi.as_view()),
    path('report-types/', UserRoleReportTypesListApi.as_view()),
    path('units/', UserRoleUnitsListApi.as_view()),
    path('', SetUserRoleApi.as_view()),

]

urlpatterns = [
    path('users/<int:chat_id>/', include(user_roles_urlpatterns)),
]
