from django.urls import path

from write_offs.views import (
    IngredientWriteOffBatchWriteOffApi,
    IngredientWriteOffListCreateApi,
    IngredientWriteOffBatchDeleteApi,
    IngredientListApi,
)


urlpatterns = [
    path('ingredients/', IngredientListApi.as_view()),
    path(r'', IngredientWriteOffListCreateApi.as_view()),
    path(
        r'batch-write-off/',
        IngredientWriteOffBatchWriteOffApi.as_view()
    ),
    path(
        r'batch-delete/',
        IngredientWriteOffBatchDeleteApi.as_view(),
    ),
]
