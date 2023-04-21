from django.db.models import QuerySet

from core.exceptions import NotFoundError
from units.models import Unit, Department


def get_units(*, limit: int, offset: int) -> QuerySet[Unit]:
    return Unit.objects.select_related('region')[offset:offset + limit]


def get_unit_by_name(name: str) -> Unit:
    try:
        return Unit.objects.select_related('region').get(name=name)
    except Unit.DoesNotExist:
        raise NotFoundError('Unit by name is not found')


def get_unit_by_id(unit_id: int) -> Unit:
    try:
        return Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        raise NotFoundError('Unit by ID is not found')


def get_departments_by_unit_office_manager_account_name(
        *,
        office_manager_account_name: str,
        limit: int | None = None,
        offset: int | None = None,
) -> QuerySet[Department]:
    departments = (
        Department.objects.filter(
            unit__office_manager_account_name=office_manager_account_name
        )
        .distinct()
    )
    if limit is not None and offset is not None:
        departments = departments[offset:limit | offset]
    return departments
