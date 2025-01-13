from celery import shared_task

from accounts.models import AccountCookies, AccountTokens
from accounts.services.auth.api_tokens import APITokensRefreshInteractor
from accounts.services.auth.office_manager import (
    OfficeManagerAccountCookiesRefreshInteractor,
)
from accounts.services.auth.shift_manager import \
    ShiftManagerAccountCookiesRefreshInteractor
from units.models import Unit


@shared_task
def refresh_office_manager_accounts_cookies():
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
        department_uuid = account_name_to_department_uuid[account_cookies.name]

        interactor = OfficeManagerAccountCookiesRefreshInteractor(
            account_cookies=account_cookies,
            department_uuid=department_uuid,
        )
        interactor.execute()


@shared_task
def refresh_shift_manager_accounts_cookies():
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


@shared_task
def refresh_api_tokens():
    accounts_tokens = AccountTokens.objects.all()
    for account_tokens in accounts_tokens:
        APITokensRefreshInteractor(account_tokens=account_tokens).execute()
