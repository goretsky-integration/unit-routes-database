from django.core.management import BaseCommand

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from reports.services.gateways.dodo_is_api import get_dodo_is_api_gateway
from write_offs.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        accounts_tokens = AccountTokens.objects.all()
        for account_tokens in accounts_tokens:
            access_token = decrypt_string(
                account_tokens.encrypted_access_token,
            )
            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                for stock_items in dodo_is_api_gateway.get_stock_items():
                    ingredients = [
                        Ingredient(
                            id=item.id,
                            name=item.name,
                        )
                        for item in stock_items
                    ]
                    Ingredient.objects.bulk_create(
                        ingredients,
                        ignore_conflicts=True,
                    )
        self.stdout.write(
            self.style.SUCCESS('Ingredients loaded successfully'),
        )
