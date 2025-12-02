from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.services.crypt import decrypt_string
from reports.services.formatters.delivery import \
    format_heated_shelf_time_statistics_report
from reports.services.gateways.dodo_is_api import (
    get_dodo_is_api_gateway,
)
from reports.services.period import Period
from reports.use_cases.create_report import CreateReportUseCase
from telegram.services import batch_create_telegram_messages


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateHeatedShelfStatisticsReport(CreateReportUseCase):
    timezone: ZoneInfo = ZoneInfo('Europe/Moscow')

    def execute(self) -> None:
        all_units = []

        today = Period.today_to_this_time()

        orders_handover_statistics = []
        couriers_orders = []

        for account_tokens, units in self.get_account_tokens_and_units():
            all_units += units

            unit_ids = {unit.uuid for unit in units}

            access_token = decrypt_string(
                account_tokens.encrypted_access_token,
            )
            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                orders_handover_statistics += dodo_is_api_gateway.get_orders_handover_statistics(
                    date_from=today.start,
                    date_to=today.end,
                    unit_ids=unit_ids,
                )
                couriers_orders += dodo_is_api_gateway.get_couriers_orders(
                    date_from=today.start,
                    date_to=today.end,
                    unit_ids=unit_ids,
                )

        text = format_heated_shelf_time_statistics_report(
            units=all_units,
            couriers_orders=couriers_orders,
            units_orders_handover_statistics=orders_handover_statistics,
        )
        batch_create_telegram_messages(
            chat_ids=[self.chat_id],
            text=text,
        )
