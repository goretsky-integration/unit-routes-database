from django.core.management import BaseCommand

from accounts.models import AccountCookies
from accounts.services.auth.office_manager import (
    OfficeManagerAccountCookiesRefreshInteractor,
)
from units.models import Unit


class Command(BaseCommand):
    help = 'Refresh office manager accounts cookies'

    def handle(self, *args, **options):
        units = Unit.objects.select_related('department').all()

        account_name_to_department_uuid = {
            unit.office_manager_account_name: unit.department.uuid
            for unit in units
            if unit.office_manager_account_name is not None
        }

        accounts_cookies = (
            AccountCookies.objects
            .select_related('account')
            .filter(name__in=account_name_to_department_uuid.keys())
            .all()
        )

        for account_cookies in accounts_cookies:
            department_uuid = account_name_to_department_uuid[
                account_cookies.name]

            interactor = OfficeManagerAccountCookiesRefreshInteractor(
                account_cookies=account_cookies,
                department_uuid=department_uuid,
            )
            interactor.execute()
