from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from reports.services.formatters.sales import int_gaps
from reports.services.formatters.stop_sales import (
    humanize_seconds,
    group_by_unit_id,
)
from reports.services.gateways.dodo_is_api import (
    UnitDeliveryStatistics,
    LateDeliveryVoucher, UnitOrdersHandoverStatistics, StopSaleBySalesChannel,
    UnitProductionProductivity,
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
        unit_delivery_statistics.avg_cooking_time,
    )
    average_heated_shelf_time_in_seconds = humanize_seconds(
        unit_delivery_statistics.avg_heated_shelf_time,
    )
    average_order_trip_time_in_seconds = humanize_seconds(
        unit_delivery_statistics.avg_order_trip_time,
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

    unit_id_to_count_today = defaultdict(int)
    for voucher in vouchers_for_today:
        unit_id_to_count_today[voucher.unit_id] += 1

    unit_id_to_count_week_before = defaultdict(int)
    for voucher in vouchers_for_week_before:
        unit_id_to_count_week_before[voucher.unit_id] += 1

    for unit in units:
        vouchers_today = unit_id_to_count_today[unit.uuid]
        vouchers_week_before = unit_id_to_count_week_before[unit.uuid]

        line = (
            f'{abbreviate_unit_name(unit.name)}'
            f' | {vouchers_today}'
            f' | {vouchers_week_before}'
        )
        lines.append(line)

    return '\n'.join(lines)


def format_delivery_performance(
    units: Iterable[Unit],
    today: Iterable[UnitDeliveryStatistics],
    week_before: Iterable[UnitDeliveryStatistics],
) -> str:
    lines: list[str] = [
        '<b>Заказов на курьера в час</b>',
    ]

    unit_id_to_orders_per_labor_hour_today = {
        statistics.unit_id: statistics.orders_per_courier_per_labor_hour
        for statistics in today
    }
    unit_id_to_orders_per_labor_hour_week_before = {
        statistics.unit_id: statistics.orders_per_courier_per_labor_hour
        for statistics in week_before
    }

    result: list[tuple[str, float, float]] = []
    for unit in units:
        orders_per_labor_hour_today = (
            unit_id_to_orders_per_labor_hour_today.get(unit.uuid, 0.0)
        )
        orders_per_labor_hour_week_before = (
            unit_id_to_orders_per_labor_hour_week_before.get(unit.uuid, 0.0)
        )

        if orders_per_labor_hour_week_before == 0:
            orders_growth_in_percents = (
                100 if orders_per_labor_hour_today > 0 else 0
            )
        else:
            orders_growth_in_percents = round(
                (
                    (
                        orders_per_labor_hour_today - orders_per_labor_hour_week_before)
                    / orders_per_labor_hour_week_before
                ) * 100,
            )
        result.append(
            (
                unit.name,
                orders_per_labor_hour_today,
                orders_growth_in_percents,
            ),
        )

    result.sort(key=lambda x: x[1])
    for unit_name, today, week_before in result:
        lines.append(
            f'{unit_name}'
            f' | {int_gaps(round(today, 1))}'
            f' | {week_before:+}%',
        )

    return '\n'.join(lines)


def format_cooking_time(
    header: str,
    units: Iterable[Unit],
    units_orders_handover_statistics: Iterable[UnitOrdersHandoverStatistics],
) -> str:
    lines: list[str] = [f'<b>{header}</b>']
    unit_id_to_cooking_time = {
        statistics.unit_id: statistics.avg_tracking_pending_time + statistics.avg_cooking_time
        for statistics in units_orders_handover_statistics
    }

    for unit in units:
        cooking_time_in_seconds = unit_id_to_cooking_time.get(unit.uuid, 0)
        humanized_cooking_time = humanize_seconds(cooking_time_in_seconds)
        lines.append(f'{unit.name} | {humanized_cooking_time}')

    return '\n'.join(lines)


def format_restaurant_cooking_time_report(
    units: Iterable[Unit],
    units_orders_handover_statistics: Iterable[UnitOrdersHandoverStatistics],
) -> str:
    return format_cooking_time(
        header='<b>Время приготовления в ресторане</b>',
        units=units,
        units_orders_handover_statistics=units_orders_handover_statistics,
    )


def format_delivery_cooking_time_report(
    units: Iterable[Unit],
    units_orders_handover_statistics: Iterable[UnitOrdersHandoverStatistics],
) -> str:
    return format_cooking_time(
        header='<b>Время приготовления на доставку</b>',
        units=units,
        units_orders_handover_statistics=units_orders_handover_statistics,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class UnitAwaitingOrdersStatistics:
    unit_name: str
    heated_shelf_orders_count: int
    couriers_in_queue_count: int
    couriers_on_shift_count: int


def format_awaiting_orders_statistics_report(
    # *,
) -> str:
    lines = ['<b>Остывают на полке - В очереди (Всего)</b>']
    lines += [
        f'{unit.unit_name} | {unit.heated_shelf_orders_count}'
        f' - {unit.couriers_in_queue_count} ({unit.couriers_on_shift_count})'
        for unit in units_statistics
    ]
    return '\n'.join(lines)
