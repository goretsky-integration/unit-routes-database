import datetime
from typing import TypeAlias, Final

import humanize
from django.utils import timezone

from reports.services.gateways.dodo_is_api import (
    StopSaleBySalesChannel,
    SalesChannel,
)


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


def compute_duration(started_at: datetime.datetime) -> datetime.timedelta:
    return timezone.localtime() + datetime.timedelta(hours=3) - started_at


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
):
    stop_sale_duration = compute_duration(started_at)
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
) -> str:
    header = render_stop_sale_header(
        unit_name=stop_sale.unit_name,
        started_at=stop_sale.started_at,
    )
    channel_name = SALES_CHANNEL_TO_NAME[stop_sale.sales_channel]
    return (
        f'{header}\n'
        f'Тип продажи: {channel_name}\n'
        f'Причина: {stop_sale.reason}'
    )
