from django.core.management import BaseCommand

from accounts.models import AccountCookies
from accounts.services.auth.shift_manager import (
    ShiftManagerAccountCookiesRefreshInteractor,
)
from units.models import Unit


class Command(BaseCommand):
    help = 'Refresh shift manager accounts cookies'

    def handle(self, *args, **options):
        units = Unit.objects.all()

        account_name_to_unit_uuid = {
            unit.shift_manager_account_name: unit.uuid
            for unit in units
            if unit.shift_manager_account_name is not None
        }

        accounts_cookies = (
            AccountCookies.objects
            .select_related('account')
            .filter(name__in=account_name_to_unit_uuid.keys())
            .all()
        )

        for account_cookies in accounts_cookies:
            unit_uuid = account_name_to_unit_uuid[account_cookies.name]

            interactor = ShiftManagerAccountCookiesRefreshInteractor(
                account_cookies=account_cookies,
                unit_uuid=unit_uuid,
            )
            interactor.execute()
