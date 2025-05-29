from uuid import UUID

from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework import serializers, status

from units.models import Unit
from write_offs.models import IngredientWriteOff, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientListApi(ListAPIView):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            'ingredients': response.data,
        }
        return response


class IngredientWriteOffCreateSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    unit_id = serializers.PrimaryKeyRelatedField(
        source='unit',
        queryset=Unit.objects.all()
    )

    class Meta:
        model = IngredientWriteOff
        fields = [
            'ingredient_id',
            'unit_id',
            'to_write_off_at',
        ]


class IngredientWriteOffListSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(
        source='unit',
        read_only=True
    )

    class Meta:
        model = IngredientWriteOff
        fields = [
            'id',
            'ingredient_name',
            'unit_id',
            'to_write_off_at',
            'written_off_at',
            'created_at',
        ]



class IngredientWriteOffBatchWriteOffDeleteSerializer(serializers.Serializer):
    ingredient_write_off_ids = serializers.ListField(
        child=serializers.UUIDField(),
    )


class IngredientWriteOffListCreateApi(ListCreateAPIView):
    queryset = IngredientWriteOff.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IngredientWriteOffCreateSerializer
        return IngredientWriteOffListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        to_write_off_date = self.request.query_params.get('date')
        unit_id = self.request.query_params.get('unit_id')
        if to_write_off_date:
            queryset = queryset.filter(to_write_off_at__date=to_write_off_date)
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            'ingredient_write_offs': response.data,
        }
        return response


class IngredientWriteOffBatchWriteOffApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = IngredientWriteOffBatchWriteOffDeleteSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        write_off_ids: list[UUID] = (
            serializer.validated_data['ingredient_write_off_ids']
        )
        IngredientWriteOff.objects.filter(id__in=write_off_ids).update(
            written_off_at=timezone.now(),
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientWriteOffBatchDeleteApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = IngredientWriteOffBatchWriteOffDeleteSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        write_off_ids: list[UUID] = (
            serializer.validated_data['ingredient_write_off_ids']
        )

        IngredientWriteOff.objects.filter(id__in=write_off_ids).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
