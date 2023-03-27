from django.db.models import QuerySet

from core.exceptions import NotFoundError
from units.models import Region, Unit


def get_regions(*, limit: int, offset: int) -> QuerySet[Region]:
    return Region.objects.all()[offset:offset + limit]


def get_units(*, limit: int, offset: int) -> QuerySet[Unit]:
    return Unit.objects.select_related('region')[offset:offset + limit]


def get_unit_by_name(name: str) -> Unit:
    return Unit.objects.select_related('region').filter(name=name).first()


def get_unit_by_id(unit_id: int) -> Unit:
    try:
        return Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        raise NotFoundError('Unit by ID is not found')


def get_region_names() -> list[str]:
    return get_regions().values_list('name', flat=True)
