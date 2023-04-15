from django.db.models import QuerySet

from accounts.models import Account


def get_accounts(
        *,
        limit: int | None = None,
        offset: int | None = None,
) -> QuerySet[Account]:
    accounts = Account.objects.prefetch_related('roles')
    if limit is not None and offset is not None:
        accounts = accounts[offset:limit + offset]
    return accounts
