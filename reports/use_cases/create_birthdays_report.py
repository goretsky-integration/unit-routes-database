from dataclasses import dataclass

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.services.filters.staff_members import (
    filter_birthdays_by_full_name,
)
from reports.services.formatters.staff_members import (
    format_birthday_congratulations,
)
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from reports.services.period import Period
from telegram.services import (
    batch_create_telegram_messages,
)
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateEmployeeBirthdaysReport:

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()
        today = Period.today_to_this_time()

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            unit_ids = {unit.uuid for unit in units}

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                birthdays = dodo_is_api_gateway.get_staff_members_birthdays(
                    day_from=today.start.day,
                    month_from=today.start.month,
                    day_to=today.end.day,
                    month_to=today.end.month,
                    unit_ids=unit_ids,
                )

            birthdays = filter_birthdays_by_full_name(birthdays)

            if not birthdays:
                continue

            text = format_birthday_congratulations(birthdays)
            batch_create_telegram_messages(
                chat_ids=[-1002038824379],
                text=text,
            )
