from dataclasses import dataclass

__all__ = (
    'ReportType',
)


@dataclass(frozen=True, slots=True)
class ReportType:
    id: int
    name: str
    verbose_name: str
