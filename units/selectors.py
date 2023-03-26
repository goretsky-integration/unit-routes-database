from django.db.models import QuerySet

from units.models import Region, Unit


def get_regions() -> QuerySet[Region]:
    return Region.objects.all()


def get_units(*, limit: int, offset: int) -> QuerySet[Unit]:
    return Unit.objects.select_related('region')[offset:offset + limit]


def get_unit_by_name(name: str) -> Unit:
    return Unit.objects.select_related('region').filter(name=name).first()


def get_region_names() -> list[str]:
    return get_regions().values_list('name', flat=True)
