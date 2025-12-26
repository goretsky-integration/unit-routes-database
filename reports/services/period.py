import datetime
from dataclasses import dataclass
from typing import Self
from zoneinfo import ZoneInfo


@dataclass(frozen=True, slots=True, kw_only=True)
class Period:
    start: datetime.datetime
    end: datetime.datetime

    def rounded_to_upper_hour(self) -> Self:
        rounded_end = self.end.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        if rounded_end < self.end:
            rounded_end += datetime.timedelta(hours=1)
        return Period(
            start=self.start,
            end=rounded_end,
        )

    @classmethod
    def today_to_this_time(cls, timezone: ZoneInfo | None = None) -> Self:
        now = datetime.datetime.now(timezone)
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
    def today_full_day(cls, timezone: ZoneInfo | None = None) -> Self:
        now = datetime.datetime.now(timezone)
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
    def yesterday_to_this_time(cls, timezone: ZoneInfo | None = None) -> Self:
        today = cls.today_to_this_time(timezone)
        return cls(
            start=today.start - datetime.timedelta(days=1),
            end=today.end - datetime.timedelta(days=1),
        )

    @classmethod
    def week_before_to_this_time(
        cls,
        timezone: ZoneInfo | None = None,
    ) -> Self:
        today = cls.today_to_this_time(timezone)
        return cls(
            start=today.start - datetime.timedelta(days=7),
            end=today.end - datetime.timedelta(days=7),
        )
