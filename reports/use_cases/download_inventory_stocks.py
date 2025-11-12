from pydantic import TypeAdapter

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.models.inventory_stocks import InventoryStocks
from reports.services.gateways.dodo_is_api import (
    get_dodo_is_api_gateway,
    InventoryStockItem,
)
from units.models import Unit


class DownloadInventoryStocksUseCase:

    def execute(self) -> None:
        type_adapter = TypeAdapter(list[InventoryStockItem])
        accounts_tokens = AccountTokens.objects.select_related('account').all()

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            unit_ids = {unit.uuid for unit in units}

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                inventory_stocks = dodo_is_api_gateway.get_inventory_stocks(
                    unit_ids=unit_ids,
                )
                InventoryStocks.objects.create(
                    data=type_adapter.dump_json(inventory_stocks),
                )
