from django.urls import path, include, register_converter

from user_roles.views import (
    UserRoleUnitsListApi,
    UserRoleRegionsListApi,
    UserRoleReportTypesListApi,
    SetUserRoleApi,
)
from core.converters import AnyIntConverter

register_converter(AnyIntConverter, 'any_int')

user_roles_urlpatterns = [
    path('regions/', UserRoleRegionsListApi.as_view()),
    path('report-types/', UserRoleReportTypesListApi.as_view()),
    path('units/', UserRoleUnitsListApi.as_view()),
    path('', SetUserRoleApi.as_view()),
]

urlpatterns = [
    path('users/<any_int:chat_id>/', include(user_roles_urlpatterns)),
]
