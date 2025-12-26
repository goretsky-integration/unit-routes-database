from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.services.formatters.inventory_stocks import (
    group_inventory_stocks,
    compute_balance_in_money_sum,
)
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from reports.services.gateways.google_sheets import (
    get_inventory_stocks_balance_spreadsheet,
    InventoryStocksBalanceGoogleSheetsGateway,
)
from units.models import Unit


class CreateInventoryStocksBalanceReportUseCase:

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()

        spreadsheet = get_inventory_stocks_balance_spreadsheet()

        units_balances = []

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            unit_ids = {unit.uuid for unit in units}

            access_token = decrypt_string(account_token.encrypted_access_token)

            inventory_stocks = []
            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                for unit_id in unit_ids:
                    for stocks in dodo_is_api_gateway.get_inventory_stocks(unit_ids=[unit_id]):
                        inventory_stocks += stocks
            units_stocks = group_inventory_stocks(inventory_stocks)

            units_balances += compute_balance_in_money_sum(units_stocks)

        gateway = InventoryStocksBalanceGoogleSheetsGateway(
            spreadsheet=spreadsheet,
        )
        gateway.write_data(units_balances)
