from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.services.formatters.delivery import format_delivery_performance
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from reports.services.period import Period
from telegram.services import batch_create_telegram_messages
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateDeliveryPerformanceReportUseCase:
    chat_id: int
    timezone: ZoneInfo = ZoneInfo("Europe/Moscow")

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()
        today = Period.today_to_this_time(self.timezone)
        week_before = Period.week_before_to_this_time(self.timezone)

        today_data = []
        week_before_data = []

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
                today_data += dodo_is_api_gateway.get_delivery_statistics(
                    date_from=today.start,
                    date_to=today.end,
                    unit_ids=unit_ids,
                )
                week_before_data += dodo_is_api_gateway.get_delivery_statistics(
                    date_from=week_before.start,
                    date_to=week_before.end,
                    unit_ids=unit_ids,
                )

        text = format_delivery_performance(
            today=today_data,
            week_before=week_before_data,
            units=all_units,
        )
        batch_create_telegram_messages(
            chat_ids=[self.chat_id],
            text=text,
        )
