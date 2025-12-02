from dataclasses import dataclass

from reports.use_cases.create_report import CreateReportUseCase


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateAwaitingOrdersReportUseCase(CreateReportUseCase):

    def execute(self) -> None:
        pass
