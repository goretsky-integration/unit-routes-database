import logging
from dataclasses import dataclass

from accounts.models import AccountCookies
from accounts.services.crypt import decrypt_dict
from units.models import Unit


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCanceledOrdersReportUseCase:

    def execute(self) -> None:
        accounts_cookies = (
            AccountCookies.objects
            .filter(name__startswith='shift_')
            .select_related('account')
        )
        units = Unit.objects.all()
        account_name_to_unit = {
            unit.shift_manager_account_name: unit
            for unit in units
        }

        for account_cookies in accounts_cookies:
            if account_cookies.account.name not in account_name_to_unit:
                logger.warning(
                    "No unit found for account: %s",
                    account_cookies.account.name
                )
                continue

            unit = account_name_to_unit[account_cookies.account.name]
            cookies = decrypt_dict(account_cookies.encrypted_cookies)

            print(unit, cookies)