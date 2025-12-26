from dataclasses import dataclass

from accounts.models import AccountTokens
from reports.models.report_routes import ReportRoute
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateReportUseCase:
    chat_id: int

    def get_units(self) -> list[Unit]:
        routes = (
            ReportRoute.objects
            .filter(telegram_chat__chat_id=self.chat_id, report_type_id=1)
            .only('unit')
        )
        return [
            route.unit for route in routes
        ]

    def get_account_tokens_and_units(self) -> list[
        tuple[AccountTokens, list[Unit]]]:
        units = self.get_units()
        account_name_to_units: dict[str, list[Unit]] = {}
        for unit in units:
            account_name_to_units.setdefault(
                unit.dodo_is_api_account_name,
                [],
            ).append(unit)

        account_tokens_and_units: list[tuple[AccountTokens, list[Unit]]] = []
        for account_token in AccountTokens.objects.select_related(
            'account',
        ).all():
            account_units = account_name_to_units.get(
                account_token.account.name,
                [],
            )
            if account_units:
                account_tokens_and_units.append(
                    (account_token, account_units),
                )

        return account_tokens_and_units
