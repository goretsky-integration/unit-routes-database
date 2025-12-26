from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.services.crypt import decrypt_string
from reports.services.formatters.sales import \
    format_productivity_balance_report
from reports.services.gateways.dodo_is_api import (
    get_dodo_is_api_gateway,
)
from reports.services.period import Period
from reports.use_cases.create_report import CreateReportUseCase
from telegram.services import batch_create_telegram_messages


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateProductivityBalanceReportUseCase(CreateReportUseCase):
    timezone: ZoneInfo = ZoneInfo('Europe/Moscow')

    def execute(self) -> None:
        all_units = []

        today = Period.today_to_this_time()
        today_rounded = today.rounded_to_upper_hour()

        production_productivity = []
        delivery_statistics = []
        stop_sales = []

        for account_tokens, units in self.get_account_tokens_and_units():
            all_units += units

            unit_ids = {unit.uuid for unit in units}

            access_token = decrypt_string(
                account_tokens.encrypted_access_token,
            )
            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                production_productivity += dodo_is_api_gateway.get_production_productivity(
                    date_from=today_rounded.start,
                    date_to=today_rounded.end,
                    unit_ids=unit_ids,
                )
                delivery_statistics += dodo_is_api_gateway.get_delivery_statistics(
                    date_from=today.start,
                    date_to=today.end,
                    unit_ids=unit_ids,
                )
                stop_sales += dodo_is_api_gateway.get_stop_sales_by_sales_channels(
                    date_from=today.start,
                    date_to=today.end,
                    unit_ids=unit_ids,
                )

        text = format_productivity_balance_report(
            units=all_units,
            production_productivity=production_productivity,
            delivery_statistics=delivery_statistics,
            stop_sales=stop_sales,
            timezone=self.timezone,
        )
        batch_create_telegram_messages(
            chat_ids=[self.chat_id],
            text=text,
        )
