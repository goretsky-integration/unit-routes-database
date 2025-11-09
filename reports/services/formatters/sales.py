from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from reports.services.gateways.dodo_is_api import UnitSales
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
        key=lambda unit_sales: unit_sales.sales_for_today
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
        f' | {units_sales_statistics.sales_growth_from_week_before_in_percents:+}%</b>'
    )

    return '\n'.join(lines)
