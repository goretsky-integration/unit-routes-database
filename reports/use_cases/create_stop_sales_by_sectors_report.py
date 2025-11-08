from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.models.report_routes import ReportRoute
from reports.services.filters.stop_sales import filter_not_ended_stop_sales
from reports.services.formatters.stop_sales import (
    format_stop_sales_by_sectors,
    group_by_unit_id,
)
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from reports.services.period import Period
from telegram.services import batch_create_telegram_messages
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateStopSalesBySectorsReport:
    timezone = ZoneInfo('UTC')

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
                stop_sales = dodo_is_api_gateway.get_stop_sales_by_sectors(
                    unit_ids=unit_ids,
                    date_from=today.start,
                    date_to=today.end,
                )

            stop_sales = filter_not_ended_stop_sales(stop_sales)

            units_stop_sales = group_by_unit_id(stop_sales)

            for unit_stop_sales in units_stop_sales:
                unit_name = unit_id_to_name.get(unit_stop_sales.unit_id, '?')
                text = format_stop_sales_by_sectors(
                    unit_name=unit_name,
                    stop_sales=unit_stop_sales.stop_sales,
                    timezone=self.timezone,
                )

                chat_ids = (
                    ReportRoute.objects
                    .filter(
                        report_type__name='SECTOR_STOP_SALES',
                        unit__uuid=unit_stop_sales.unit_id,
                    )
                    .values_list('telegram_chat__chat_id', flat=True)
                )
                batch_create_telegram_messages(
                    chat_ids=chat_ids,
                    text=text,
                )
