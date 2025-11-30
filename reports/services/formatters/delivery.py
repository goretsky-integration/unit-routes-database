from collections.abc import Iterable

from reports.services.formatters.stop_sales import (
    humanize_seconds,
    group_by_unit_id,
)
from reports.services.gateways.dodo_is_api import (
    UnitDeliveryStatistics,
    LateDeliveryVoucher,
)
from units.models import Unit


def abbreviate_unit_name(unit_name: str) -> str:
    """Contract department name via abbreviations.

    Examples:
        >>> abbreviate_unit_name('Москва 4-1')
        '4-1'
        >>> abbreviate_unit_name('Вязьма-2')
        'ВЗМ-2'
        >>> abbreviate_unit_name('Калуга-4')
        'КЛ-4'

    Args:
        unit_name: Unit name.

    Returns:
        Contracted department name or department name itself without changes
        if department name is not in special replacing map.
    """
    replacing_map = (
        ('вязьма', 'ВЗМ'),
        ('калуга', 'КЛ'),
        ('смоленск', 'СМ'),
        ('обнинск', 'ОБН'),
        ('москва', ''),
        ('подольск', 'П'),
    )
    unit_name = unit_name
    for replaceable, replace_to in replacing_map:
        if replaceable in unit_name.lower():
            return unit_name.lower().replace(replaceable, replace_to).lstrip()
    return unit_name


def format_unit_delivery_speed_statistics(
    unit_delivery_statistics: UnitDeliveryStatistics,
) -> str:
    unit_name = abbreviate_unit_name(unit_delivery_statistics.unit_name)
    average_delivery_order_fulfillment_time_in_seconds = humanize_seconds(
        unit_delivery_statistics.avg_delivery_order_fulfillment_time,
    )
    average_cooking_time_in_seconds = humanize_seconds(
        unit_delivery_statistics.avg_cooking_time_in_seconds,
    )
    average_heated_shelf_time_in_seconds = humanize_seconds(
        unit_delivery_statistics.avg_heated_shelf_time_in_seconds,
    )
    average_order_trip_time_in_seconds = humanize_seconds(
        unit_delivery_statistics.avg_order_trip_time_in_seconds,
    )
    return (
        f'{unit_name}'
        f' | {average_delivery_order_fulfillment_time_in_seconds}'
        f' | {average_cooking_time_in_seconds}'
        f' | {average_heated_shelf_time_in_seconds}'
        f' | {average_order_trip_time_in_seconds}'
    )


def format_delivery_speed_report(
    units_delivery_statistics: Iterable[UnitDeliveryStatistics],
) -> str:
    lines: list[str] = [
        '<b>'
        'Общая скорость доставки'
        ' - Время приготовления'
        ' - Время на полке'
        ' - Поездка курьера'
        '</b>',
    ]

    units = sorted(
        units_delivery_statistics,
        key=lambda x: x.avg_delivery_order_fulfillment_time,
    )

    for unit_delivery_statistics in units:
        line = format_unit_delivery_speed_statistics(
            unit_delivery_statistics,
        )
        lines.append(line)

    return '\n'.join(lines)


def format_delivery_vouchers_report(
    units: Iterable[Unit],
    vouchers_for_today: Iterable[LateDeliveryVoucher],
    vouchers_for_week_before: Iterable[LateDeliveryVoucher],
) -> str:
    lines = ['<b>Сертификаты за опоздание (сегодня) | (неделю назад)</b>']

    unit_id_to_vouchers_for_today = group_by_unit_id(vouchers_for_today)
    unit_id_to_vouchers_for_week_before = group_by_unit_id(
        vouchers_for_week_before,
    )

    for unit in units:
        vouchers_today = unit_id_to_vouchers_for_today.get(unit.uuid, [])
        vouchers_week_before = unit_id_to_vouchers_for_week_before.get(
            unit.uuid, [],
        )
        line = (
            f'{abbreviate_unit_name(unit.name)}'
            f' | {len(vouchers_today)}'
            f' | {len(vouchers_week_before)}'
        )
        lines.append(line)

    return '\n'.join(lines)