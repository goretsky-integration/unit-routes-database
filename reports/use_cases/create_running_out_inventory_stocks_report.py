from dataclasses import dataclass

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.services import get_dodo_is_api_gateway
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateRunningOutInventoryStocksReportUseCase:

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                inventory_stocks = dodo_is_api_gateway.get_inventory_stocks(
                    unit_ids=[unit.uuid for unit in units],
                )

                print(inventory_stocks)
