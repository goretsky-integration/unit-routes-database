from django.urls import path

from units.views import (
    UnitsListApi,
    UnitRetrieveByNameApi,
    UnitDepartmentsListApi,
)

urlpatterns = [
    path('', UnitsListApi.as_view()),
    path('name/<str:unit_name>/', UnitRetrieveByNameApi.as_view()),
    path('departments/', UnitDepartmentsListApi.as_view())
]
