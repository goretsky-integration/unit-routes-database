from dataclasses import dataclass

__all__ = (
    'ReportRoute',
    'ReportChatIdAndUnitIds',
    'GroupedByReportTypeAndChatIDReportRoute',
)


@dataclass(frozen=True, slots=True)
class ReportRoute:
    report_type_name: str
    chat_id: int
    unit_id: int


@dataclass(frozen=True, slots=True)
class GroupedByReportTypeAndChatIDReportRoute:
    report_type: str
    chat_id: int
    unit_ids: list[int]


@dataclass(frozen=True, slots=True)
class ReportChatIdAndUnitIds:
    chat_id: int
    unit_ids: list[int]
