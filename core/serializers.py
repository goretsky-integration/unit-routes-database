from rest_framework import serializers


class LimitOffsetSerializer(serializers.Serializer):
    limit = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=100,
    )
    offset = serializers.IntegerField(
        min_value=0,
        default=0,
    )
