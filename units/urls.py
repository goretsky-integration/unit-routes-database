from django.urls import path

from units.views import (
    UnitsListApi,
    UnitRegionsListApi,
    UnitRetrieveByNameApi,
    UnitDepartmentsListApi,
)

urlpatterns = [
    path('', UnitsListApi.as_view()),
    path('name/<str:unit_name>/', UnitRetrieveByNameApi.as_view()),
    path('regions/', UnitRegionsListApi.as_view()),
    path('departments/', UnitDepartmentsListApi.as_view())
]
