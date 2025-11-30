from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.services.formatters.delivery import (
    format_delivery_vouchers_report,
)
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from reports.services.period import Period
from telegram.services import batch_create_telegram_messages
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateDeliverySpeedReportUseCase:
    chat_id: int
    timezone: ZoneInfo = ZoneInfo("Europe/Moscow")

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()
        today = Period.today_to_this_time(self.timezone)
        week_before = Period.week_before_to_this_time(self.timezone)

        vouchers_for_today = []
        vouchers_for_week_before = []
        all_units = []
        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            all_units += units

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                vouchers_for_today += dodo_is_api_gateway.get_delivery_vouchers(
                    date_from=today.start,
                    date_to=today.end,
                    unit_ids={unit.uuid for unit in units},
                )
                vouchers_for_week_before += dodo_is_api_gateway.get_delivery_vouchers(
                    date_from=week_before.start,
                    date_to=week_before.end,
                    unit_ids={unit.uuid for unit in units},
                )

        text = format_delivery_vouchers_report(
            units=all_units,
            vouchers_for_today=vouchers_for_today,
            vouchers_for_week_before=vouchers_for_week_before,
        )
        batch_create_telegram_messages(
            chat_ids=[self.chat_id],
            text=text,
        )
