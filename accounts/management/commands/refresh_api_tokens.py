from django.core.management import BaseCommand

from accounts.models import AccountTokens
from accounts.services.auth.api_tokens import APITokensRefreshInteractor


class Command(BaseCommand):
    help = 'Refresh API tokens'

    def handle(self, *args, **options):
        accounts_tokens = AccountTokens.objects.all()
        for account_tokens in accounts_tokens:
            APITokensRefreshInteractor(account_tokens=account_tokens).execute()
