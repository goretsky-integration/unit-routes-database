from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.models.report_routes import ReportRoute
from reports.services.filters.stop_sales import (
    filter_stop_sales_by_sales_channels,
)
from reports.services.formatters.stop_sales import (
    format_stop_sale_by_sales_channel,
)
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from reports.services.period import Period
from telegram.services import batch_create_telegram_messages
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateStopSalesBySalesChannelsReport:
    timezone = ZoneInfo('Europe/Moscow')

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()
        today = Period.today_to_this_time(self.timezone)

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            unit_ids = {unit.uuid for unit in units}

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                stop_sales = dodo_is_api_gateway.get_stop_sales_by_sales_channels(
                    unit_ids=unit_ids,
                    date_from=today.start,
                    date_to=today.end,
                )

            stop_sales = filter_stop_sales_by_sales_channels(stop_sales)

            for stop_sale in stop_sales:
                text = format_stop_sale_by_sales_channel(stop_sale)

                chat_ids = (
                    ReportRoute.objects
                    .filter(
                        report_type__name='PIZZERIA_STOP_SALES',
                        unit__uuid=stop_sale.unit_id,
                    )
                    .values_list('telegram_chat__chat_id', flat=True)
                )
                batch_create_telegram_messages(
                    chat_ids=chat_ids,
                    text=text,
                )
