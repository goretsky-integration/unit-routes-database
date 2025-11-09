from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.services.formatters.sales import (
    group_sales,
    format_sales_statistics,
)
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from reports.services.period import Period
from telegram.services import batch_create_telegram_messages
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateDailyRevenueReportUseCase:
    chat_id: int
    timezone: ZoneInfo = ZoneInfo("Europe/Moscow")

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()
        today = Period.today_to_this_time(self.timezone)
        week_before = Period.week_before_to_this_time(self.timezone)

        today_sales = []
        week_before_sales = []

        all_units = []

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            all_units += units
            unit_ids = {unit.uuid for unit in units}

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                today_sales += dodo_is_api_gateway.get_units_sales_for_period(
                    date_from=today.start,
                    date_to=today.end,
                    unit_ids=unit_ids,
                )
                week_before_sales += dodo_is_api_gateway.get_units_sales_for_period(
                    date_from=week_before.start,
                    date_to=week_before.end,
                    unit_ids=unit_ids,
                )

        sales_statistics = group_sales(
            units=all_units,
            units_today_sales=today_sales,
            units_week_before_sales=week_before_sales,
        )
        text = format_sales_statistics(sales_statistics)
        batch_create_telegram_messages(
            chat_ids=[self.chat_id],
            text=text,
        )
