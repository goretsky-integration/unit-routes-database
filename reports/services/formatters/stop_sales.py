import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeAlias, Final, Protocol, TypeVar, Generic
from uuid import UUID
from zoneinfo import ZoneInfo

import humanize

from reports.services.gateways.dodo_is_api import (
    StopSaleBySalesChannel,
    SalesChannel, StopSaleByIngredient, StopSaleBySector,
)


humanize.i18n.activate("ru_RU")

SALES_CHANNEL_TO_NAME = {
    SalesChannel.DINE_IN: 'Ресторан',
    SalesChannel.TAKEAWAY: 'Самовывоз',
    SalesChannel.DELIVERY: 'Доставка',
}

MINUTE_IN_SECONDS: Final[int] = 60
HOUR_IN_SECONDS: Final[int] = MINUTE_IN_SECONDS * 60
DAY_IN_SECONDS: Final[int] = HOUR_IN_SECONDS * 24

TimeUnitsAndAbbreviation: TypeAlias = tuple[tuple[str, ...], str]


def abbreviate_time_units(text: str) -> str:
    time_units_and_abbreviations: tuple[TimeUnitsAndAbbreviation, ...] = (
        (('дней', 'день', 'дня'), 'дн'),
        (('часов', 'часа', 'час',), 'ч'),
        (('минута', 'минуты', 'минут'), 'мин'),
    )
    words = set(text.split())
    for time_units, abbreviation in time_units_and_abbreviations:
        for time_unit in time_units:
            if time_unit not in words:
                continue
            text = text.replace(time_unit, abbreviation)
    return text


def compute_duration(
    started_at: datetime.datetime,
    *,
    timezone: ZoneInfo | None = None,
) -> datetime.timedelta:
    if timezone is not None:
        started_at = started_at.replace(tzinfo=timezone)
    return datetime.datetime.now(timezone) - started_at


def humanize_stop_sale_duration(duration: datetime.timedelta) -> str:
    stop_duration_in_seconds = duration.total_seconds()

    if stop_duration_in_seconds >= DAY_IN_SECONDS:
        kwargs = {
            'format': '%0.0f',
            'minimum_unit': 'days',
            'suppress': ['months'],
        }
    elif stop_duration_in_seconds >= HOUR_IN_SECONDS:
        kwargs = {'format': '%0.0f', 'minimum_unit': 'hours'}
    elif stop_duration_in_seconds >= MINUTE_IN_SECONDS:
        kwargs = {'format': '%0.0f', 'minimum_unit': 'minutes'}
    else:
        kwargs = {'format': '%0.0f', 'minimum_unit': 'seconds'}

    return abbreviate_time_units(humanize.precisedelta(duration, **kwargs))


def is_urgent(duration: datetime.timedelta) -> bool:
    return duration.total_seconds() >= MINUTE_IN_SECONDS * 30


def humanize_seconds(seconds: int) -> str:
    """Humanize time in seconds.

    Examples:
        >>> humanize_seconds(60)
        '01:00'
        >>> humanize_seconds(0)
        '00:00'
        >>> humanize_seconds(3600)
        '01:00:00'
        >>> humanize_seconds(9000000)
        '+99:59:59'

    Args:
        seconds: Time in seconds.

    Returns:
        Humanized time in HH:MM:SS or MM:SS format.
        If there are over 100 hours (359999 seconds), returns "+99:59:59".
    """
    if seconds > 359999:
        return '+99:59:59'
    minutes = seconds // 60
    seconds %= 60
    hours = minutes // 60
    minutes %= 60
    if not hours:
        return f'{minutes:02}:{seconds:02}'
    return f'{hours:02}:{minutes:02}:{seconds:02}'


def render_stop_sale_header(
    *,
    unit_name: str,
    started_at: datetime.datetime,
    timezone: ZoneInfo,
):
    stop_sale_duration = compute_duration(started_at, timezone=timezone)
    humanized_stop_sale_duration = humanize_stop_sale_duration(
        duration=stop_sale_duration,
    )
    humanized_stop_sale_started_at = f'{started_at:%H:%M}'

    header = (
        f'{unit_name}'
        f' в стопе {humanized_stop_sale_duration}'
        f' (с {humanized_stop_sale_started_at})')

    if is_urgent(stop_sale_duration):
        header = '❗️ ' + header + ' ❗️'

    return header


def format_stop_sale_by_sales_channel(
    stop_sale: StopSaleBySalesChannel,
    *,
    timezone: ZoneInfo,
) -> str:
    header = render_stop_sale_header(
        unit_name=stop_sale.unit_name,
        started_at=stop_sale.started_at,
        timezone=timezone,
    )
    channel_name = SALES_CHANNEL_TO_NAME[stop_sale.sales_channel]
    return (
        f'{header}\n'
        f'Тип продажи: {channel_name}\n'
        f'Причина: {stop_sale.reason}'
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class StopSalesByIngredientsGroupedByReason:
    reason: str
    stop_sales: Iterable[StopSaleByIngredient]


class HasUnitId(Protocol):
    unit_id: UUID


HasUnitIdT = TypeVar('HasUnitIdT', bound=HasUnitId)


@dataclass(frozen=True, slots=True, kw_only=True)
class StopSalesGroupedByUnitId(Generic[HasUnitIdT]):
    unit_id: UUID
    stop_sales: Iterable[HasUnitIdT]


def group_by_unit_id(
    stop_sales: Iterable[HasUnitIdT],
) -> list[StopSalesGroupedByUnitId]:
    unit_id_to_stop_sales = defaultdict(list)
    for stop_sale in stop_sales:
        unit_id_to_stop_sales[stop_sale.unit_id].append(stop_sale)

    return [
        StopSalesGroupedByUnitId(
            unit_id=unit_id,
            stop_sales=stop_sales,
        )
        for unit_id, stop_sales in unit_id_to_stop_sales.items()
    ]


def group_by_reason(
    stop_sales: Iterable[StopSaleByIngredient],
) -> list[StopSalesByIngredientsGroupedByReason]:
    reason_to_stop_sales = defaultdict(list)
    for stop_sale in stop_sales:
        reason_to_stop_sales[stop_sale.reason].append(stop_sale)

    return [
        StopSalesByIngredientsGroupedByReason(
            reason=reason,
            stop_sales=stop_sales,
        )
        for reason, stop_sales in reason_to_stop_sales.items()
    ]


def render_stop_sale_by_ingredient(
    stop_sale: StopSaleByIngredient,
    timezone: ZoneInfo,
) -> str:
    duration = compute_duration(stop_sale.started_at, timezone=timezone)
    humanized_stop_duration = humanize_stop_sale_duration(duration)
    return (
        f'📍 {stop_sale.ingredient_name}'
        f' - <b><u>{humanized_stop_duration}</u></b>'
    )


def format_stop_sales_by_ingredients(
    *,
    unit_name: str,
    stop_sales_by_reasons: Iterable[StopSalesByIngredientsGroupedByReason],
    timezone: ZoneInfo,
) -> str:
    lines = [f'<b>{unit_name}</b>']

    if not stop_sales_by_reasons:
        lines.append(
            '<b>Стопов пока нет!'
            ' Молодцы. Ваши Клиенты довольны</b>',
        )

    for stop_sales_by_reason in stop_sales_by_reasons:
        stop_sales = sorted(
            stop_sales_by_reason.stop_sales,
            key=lambda stop_sale: stop_sale.started_at,
            reverse=True,
        )

        lines.append(f'\n<b>{stop_sales_by_reason.reason}:</b>')
        lines += [
            render_stop_sale_by_ingredient(stop_sale, timezone=timezone)
            for stop_sale in stop_sales
        ]
    return '\n'.join(lines)


def format_stop_sales_by_sectors(
    *,
    unit_name: str,
    stop_sales: Iterable[StopSaleBySector],
    timezone: ZoneInfo,
) -> str:
    stop_sales = sorted(stop_sales, key=lambda stop_sale: stop_sale.started_at)
    if len(stop_sales) == 1:
        sector_singular_or_plural = 'сектор'
    else:
        sector_singular_or_plural = 'сектора'

    lines = [f'<b>{unit_name} {sector_singular_or_plural} в стопе:</b>']

    for stop_sale in stop_sales:
        duration = compute_duration(stop_sale.started_at, timezone=timezone)
        humanized_duration = humanize_stop_sale_duration(duration)

        line = (
            f'{stop_sale.sector_name}'
            f' - {humanized_duration}'
            f' (с {stop_sale.started_at:%H:%M})'
        )

        if is_urgent(duration):
            line = f'❗️ {line} ❗️'

        lines.append(line)

    return '\n'.join(lines)
