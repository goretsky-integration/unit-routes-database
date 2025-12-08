import datetime
import json

from pydantic import TypeAdapter

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from snapshots.models import DodoIsApiResponseSnapshot
from reports.services.gateways.dodo_is_api import (
    get_dodo_is_api_gateway,
    InventoryStockItem,
)
from units.models import Unit


class DownloadInventoryStocksUseCase:

    def execute(self) -> None:
        type_adapter = TypeAdapter(list[InventoryStockItem])
        accounts_tokens = AccountTokens.objects.select_related('account').all()

        now = datetime.datetime.now(datetime.UTC)

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            unit_ids = {unit.uuid for unit in units}

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                for unit_id in unit_ids:
                    data = []
                    for i in dodo_is_api_gateway.get_inventory_stocks(
                            unit_ids=[unit_id],
                    ):
                        data += i
                    data = type_adapter.dump_python(data)
                    data = json.dumps(data, default=str)

                    DodoIsApiResponseSnapshot.objects.create(
                        name=f'inventory_stocks_unit_{unit_id}-{now.isoformat()}',
                        data=data,
                    )
