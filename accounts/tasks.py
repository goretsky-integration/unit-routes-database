from celery import shared_task

from accounts.models import AccountCookies
from accounts.selectors import get_office_manager_accounts
from accounts.services.auth.office_manager import (
    OfficeManagerAccountCookiesRefreshInteractor,
)
from units.models import Unit


@shared_task
def refresh_office_manager_accounts_cookies():
    units = Unit.objects.select_related('department').all()

    account_name_to_department_uuid = {
        unit.office_manager_account_name: unit.department.uuid
        for unit in units
    }

    accounts_cookies = (
        AccountCookies.objects
        .select_related('account')
        .filter(name__in=account_name_to_department_uuid.keys())
        .all()
    )

    for account_cookies in accounts_cookies:
        department_uuid = account_name_to_department_uuid[account_cookies.name]

        interactor = OfficeManagerAccountCookiesRefreshInteractor(
            account_cookies=account_cookies,
            department_uuid=department_uuid,
        )
        interactor.execute()
