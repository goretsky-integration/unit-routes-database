from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.models.report_routes import ReportRoute
from reports.services.filters.stop_sales import filter_not_ended_stop_sales
from reports.services.formatters.stop_sales import (
    group_by_unit_id,
    format_stop_sales_by_ingredients, group_by_reason,
    StopSalesByIngredientsGroupedByUnitId,
)
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from reports.services.period import Period
from telegram.services import batch_create_telegram_messages
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateStopSalesByAllIngredientsReport:
    timezone = ZoneInfo('Europe/Moscow')

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()
        today = Period.today_to_this_time(self.timezone)

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
                stop_sales = dodo_is_api_gateway.get_stop_sales_by_ingredients(
                    unit_ids=unit_ids,
                    date_from=today.start,
                    date_to=today.end,
                )

            stop_sales = filter_not_ended_stop_sales(stop_sales)

            existing_stop_sales_unit_ids = {stop_sale.unit_id for stop_sale in stop_sales}
            missing_unit_ids = unit_ids - existing_stop_sales_unit_ids
            missing_stop_sales = [
                StopSalesByIngredientsGroupedByUnitId(
                    unit_id=unit_id,
                    stop_sales=[],
                )
                for unit_id in missing_unit_ids
            ]

            units_stop_sales = group_by_unit_id(stop_sales) + missing_stop_sales

            for unit_stop_sales in units_stop_sales:
                unit_name = unit_id_to_name.get(unit_stop_sales.unit_id, '?')
                text = format_stop_sales_by_ingredients(
                    unit_name=unit_name,
                    stop_sales_by_reasons=group_by_reason(
                        unit_stop_sales.stop_sales,
                    ),
                )

                chat_ids = (
                    ReportRoute.objects
                    .filter(
                        report_type__name='INGREDIENTS_STOP_SALES',
                        unit__uuid=unit_stop_sales.unit_id,
                    )
                    .values_list('telegram_chat__chat_id', flat=True)
                )
                batch_create_telegram_messages(
                    chat_ids=chat_ids,
                    text=text,
                )
