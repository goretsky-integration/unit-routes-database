from dataclasses import dataclass

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.models.report_routes import ReportRoute
from reports.services import (
    get_dodo_is_api_gateway,
    filter_running_out_stock_items,
    filter_relevant_items,
    group_inventory_stocks,
    format_running_out_stock_items, get_empty_units_inventory_stocks,
)
from telegram.services import batch_create_telegram_messages
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateRunningOutInventoryStocksReportUseCase:

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            unit_ids = {unit.uuid for unit in units}
            unit_id_to_name = {unit.uuid: unit.name for unit in units}

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                inventory_stocks = dodo_is_api_gateway.get_inventory_stocks(
                    unit_ids=unit_ids,
                )
            relevant_inventory_stocks = filter_relevant_items(inventory_stocks)

            running_out_stocks = filter_running_out_stock_items(
                items=relevant_inventory_stocks,
                threshold=1,
            )
            units_stocks = group_inventory_stocks(running_out_stocks)

            unit_ids_with_running_out_stocks = {
                unit_stocks.unit_id for unit_stocks in units_stocks
            }
            empty_units_stocks = get_empty_units_inventory_stocks(
                unit_ids=unit_ids - unit_ids_with_running_out_stocks,
            )
            all_units_stocks = units_stocks + empty_units_stocks
            for unit_stocks in all_units_stocks:
                unit_name = unit_id_to_name.get(unit_stocks.unit_id, '?')

                running_out_stock_items_text = format_running_out_stock_items(
                    unit_name=unit_name,
                    items=unit_stocks.items,
                )

                chat_ids = (
                    ReportRoute.objects
                    .filter(
                        report_type__name='INVENTORY_STOCKS',
                        unit__uuid=unit_stocks.unit_id,
                    )
                    .values_list('telegram_chat__chat_id', flat=True)
                )

                batch_create_telegram_messages(
                    chat_ids=chat_ids,
                    text=running_out_stock_items_text,
                )
