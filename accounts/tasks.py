from celery import shared_task

from accounts.selectors import get_office_manager_accounts
from accounts.services.auth.office_manager import (
    OfficeManagerAccountCookiesRefreshInteractor,
)
from units.models import Unit


@shared_task
def refresh_office_manager_accounts_cookies():
    units = Unit.objects.select_related('department').all()
    accounts = get_office_manager_accounts()

    account_name_to_department_uuid = {
        unit.office_manager_account_name: unit.department.uuid
        for unit in units
    }

    for account in accounts:
        print(account.name, account_name_to_department_uuid)
        if account.name not in account_name_to_department_uuid:
            continue
        department_uuid = account_name_to_department_uuid[account.name]

        interactor = OfficeManagerAccountCookiesRefreshInteractor(
            account=account,
            department_uuid=department_uuid,
        )
        interactor.execute()
