from dataclasses import dataclass

__all__ = (
    'ReportRoute',
    'ReportChatIdAndUnitIds',
)


@dataclass(frozen=True, slots=True)
class ReportRoute:
    report_type_name: str
    telegram_chat_id: int
    unit_id: int


@dataclass(frozen=True, slots=True)
class ReportChatIdAndUnitIds:
    chat_id: int
    unit_ids: list[int]
