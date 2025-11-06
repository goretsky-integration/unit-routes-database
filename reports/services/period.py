import datetime
from dataclasses import dataclass
from typing import Self

from django.utils import timezone


@dataclass(frozen=True, slots=True, kw_only=True)
class Period:
    start: datetime.datetime
    end: datetime.datetime

    @classmethod
    def today_to_this_time(cls) -> Self:
        now = timezone.localtime() + datetime.timedelta(hours=3)
        return cls(
            start=now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            ),
            end=now,
        )

    @classmethod
    def today_full_day(cls) -> Self:
        now = timezone.localtime()
        return cls(
            start=now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            ),
            end=now.replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
            ),
        )

    @classmethod
    def yesterday_to_this_time(cls) -> Self:
        today = cls.today_to_this_time()
        return cls(
            start=today.start - datetime.timedelta(days=1),
            end=today.end - datetime.timedelta(days=1),
        )
