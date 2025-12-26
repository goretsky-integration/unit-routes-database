from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID
from zoneinfo import ZoneInfo

from reports.services.formatters.stop_sales import (
    humanize_seconds,
    compute_duration,
)
from reports.services.gateways.dodo_is_api import (
    UnitSales,
    UnitProductionProductivity, UnitDeliveryStatistics, StopSaleBySalesChannel,
    ChannelStopType,
)
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class UnitSalesForTodayAndWeekBefore:
    unit_name: str
    sales_for_today: float
    sales_growth_from_week_before_in_percents: int


@dataclass(frozen=True, slots=True, kw_only=True)
class UnitsSalesStatistics:
    units_sales: list[UnitSalesForTodayAndWeekBefore]
    total_sales_for_today: float
    sales_growth_from_week_before_in_percents: int


def group_sales(
    *,
    units: Iterable[Unit],
    units_today_sales: Iterable[UnitSales],
    units_week_before_sales: Iterable[UnitSales],
) -> UnitsSalesStatistics:
    unit_id_to_today_sales: dict[UUID, float] = {
        unit_sales.unit_id: unit_sales.sales
        for unit_sales in units_today_sales
    }
    unit_id_to_week_before_sales: dict[UUID, float] = {
        unit_sales.unit_id: unit_sales.sales
        for unit_sales in units_week_before_sales
    }

    total_sales_for_today = 0
    total_sales_for_week_before = 0

    result: list[UnitSalesForTodayAndWeekBefore] = []
    for unit in units:
        today_sales = unit_id_to_today_sales.get(unit.uuid, 0.0)
        week_before_sales = unit_id_to_week_before_sales.get(unit.uuid, 0.0)

        total_sales_for_today += today_sales
        total_sales_for_week_before += week_before_sales

        if week_before_sales == 0:
            sales_growth_in_percents = 100 if today_sales > 0 else 0
        else:
            sales_growth_in_percents = round(
                ((today_sales - week_before_sales) / week_before_sales) * 100,
            )

        result.append(
            UnitSalesForTodayAndWeekBefore(
                unit_name=unit.name,
                sales_for_today=round(today_sales, 2),
                sales_growth_from_week_before_in_percents=sales_growth_in_percents,
            ),
        )

    if total_sales_for_week_before == 0:
        total_sales_growth_in_percents = (
            100 if total_sales_for_today > 0 else 0
        )
    else:
        total_sales_growth_in_percents = round(
            (
                (total_sales_for_today - total_sales_for_week_before)
                / total_sales_for_week_before
            ) * 100,
        )

    return UnitsSalesStatistics(
        units_sales=result,
        total_sales_for_today=round(total_sales_for_today, 2),
        sales_growth_from_week_before_in_percents=total_sales_growth_in_percents,
    )


def int_gaps(number: int | float) -> str:
    """Add gaps to number.

    Examples:
        >>> int_gaps(123456789)
        '123 456 789'
        >>> int_gaps(123)
        '123'
    """
    return f'{number:,}'.replace(',', ' ')


def format_sales_statistics(
    units_sales_statistics: UnitsSalesStatistics
) -> str:
    units_sales = sorted(
        units_sales_statistics.units_sales,
        key=lambda unit_sales: unit_sales.sales_for_today,
    )

    lines: list[str] = ['<b>Выручка за сегодня</b>']
    lines += [
        f'{unit_sales.unit_name}'
        f' | {int_gaps(unit_sales.sales_for_today)}'
        f' | {unit_sales.sales_growth_from_week_before_in_percents:+}%'
        for unit_sales in units_sales
    ]
    lines.append(
        f'<b>Итого: {int_gaps(units_sales_statistics.total_sales_for_today)}'
        f' | {units_sales_statistics.sales_growth_from_week_before_in_percents:+}%</b>',
    )

    return '\n'.join(lines)


def format_production_performance_statistics(
    units: Iterable[Unit],
    today: Iterable[UnitProductionProductivity],
    week_before: Iterable[UnitProductionProductivity],
) -> str:
    lines: list[str] = [
        '<b>Выручка на чел. в час</b>',
    ]

    unit_id_to_sales_per_labor_hour_today = {
        productivity.unit_id: productivity.sales_per_labor_hour
        for productivity in today
    }
    unit_id_to_sales_per_labor_hour_week_before = {
        productivity.unit_id: productivity.sales_per_labor_hour
        for productivity in week_before
    }

    result: list[tuple[str, float, float]] = []
    for unit in units:
        sales_per_labor_hour_today = (
            unit_id_to_sales_per_labor_hour_today.get(unit.uuid, 0.0)
        )
        sales_per_labor_hour_week_before = (
            unit_id_to_sales_per_labor_hour_week_before.get(unit.uuid, 0.0)
        )

        if sales_per_labor_hour_week_before == 0:
            sales_growth_in_percents = (
                100 if sales_per_labor_hour_today > 0 else 0
            )
        else:
            sales_growth_in_percents = round(
                (
                    (
                        sales_per_labor_hour_today - sales_per_labor_hour_week_before)
                    / sales_per_labor_hour_week_before
                ) * 100,
            )
        result.append(
            (
                unit.name,
                sales_per_labor_hour_today,
                sales_growth_in_percents,
            ),
        )

    result.sort(key=lambda x: x[1])
    for unit_name, today, week_before in result:
        lines.append(
            f'{unit_name}'
            f' | {int_gaps(round(today))}'
            f' | {week_before:+}%',
        )

    return '\n'.join(lines)


@dataclass(frozen=True, slots=True, kw_only=True)
class UnitProductivityBalance:
    unit_name: str
    sales_per_labor_hour: float
    orders_per_labor_hour: float
    stop_sale_duration_in_seconds: int


def format_productivity_balance_report(
    *,
    units: Iterable[Unit],
    production_productivity: Iterable[UnitProductionProductivity],
    delivery_statistics: Iterable[UnitDeliveryStatistics],
    stop_sales: Iterable[StopSaleBySalesChannel],
    timezone: ZoneInfo,
) -> str:
    lines = ['<b>Баланс эффективности</b>']

    unit_id_to_sales_per_labor_hour_today = {
        stats.unit_id: stats.sales_per_labor_hour
        for stats in production_productivity
    }
    unit_id_to_orders_per_labor_hour: dict[UUID, float] = {
        stats.unit_id: stats.orders_per_courier_per_labor_hour
        for stats in delivery_statistics
    }
    unit_id_to_stop_sale_duration = defaultdict(int)
    for stop_sale in stop_sales:
        if stop_sale.channel_stop_type != ChannelStopType.COMPLETE:
            continue
        duration = compute_duration(
            started_at=stop_sale.started_at,
            timezone=timezone,
        )
        unit_id_to_stop_sale_duration[
            stop_sale.unit_id] += int(duration.total_seconds())

    result: list[UnitProductivityBalance] = []
    for unit in units:
        sales_per_labor_hour = (
            unit_id_to_sales_per_labor_hour_today.get(unit.uuid, 0.0)
        )
        orders_per_labor_hour = (
            unit_id_to_orders_per_labor_hour.get(unit.uuid, 0.0)
        )
        stop_sale_duration_in_seconds = (
            unit_id_to_stop_sale_duration.get(unit.uuid, 0)
        )

        result.append(
            UnitProductivityBalance(
                unit_name=unit.name,
                sales_per_labor_hour=sales_per_labor_hour,
                orders_per_labor_hour=orders_per_labor_hour,
                stop_sale_duration_in_seconds=stop_sale_duration_in_seconds,
            ),
        )

    result.sort(key=lambda x: x.sales_per_labor_hour, reverse=True)

    lines += [
        (
            f'{unit_statistics.unit_name}'
            f' | {int_gaps(unit_statistics.sales_per_labor_hour)}'
            f' | {round(unit_statistics.orders_per_labor_hour, 1)}'
            f' | {humanize_seconds(unit_statistics.stop_sale_duration_in_seconds)}'
        )
        for unit_statistics in result
    ]
    return '\n'.join(lines)
