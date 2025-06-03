from uuid import UUID

import httpx
from django.core.management import BaseCommand

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from write_offs.models import Ingredient


def batched(iterable, batch_size):
    """Yield successive n-sized chunks from iterable."""
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]


class DodoIsApiGateway:

    def __init__(self, http_client: httpx.Client):
        self.__http_client = http_client

    def get_stock_items(self, *, take: int, skip: int) -> dict:
        response = self.__http_client.get(
            'https://api.dodois.io/dodopizza/ru/accounting/stock-items',
            params={'take': take, 'skip': skip},
        )
        response.raise_for_status()
        return response.json()


class Command(BaseCommand):

    def handle(self, *args, **options):
        accounts_tokens = AccountTokens.objects.all()
        for account_tokens in accounts_tokens:
            access_token = decrypt_string(
                account_tokens.encrypted_access_token,
            )
            with httpx.Client(
                    headers={
                        'Authorization': f'Bearer {access_token}'
                    }
            ) as http_client:
                dodo_is_api_gateway = DodoIsApiGateway(http_client)

                skip = 0
                take = 1000
                while True:
                    stock_items = dodo_is_api_gateway.get_stock_items(
                        take=take,
                        skip=skip,
                    )
                    ingredients = [
                        Ingredient(
                            id=UUID(item['id']),
                            name=item['name'],
                        )
                        for item in stock_items['stockItems']
                    ]
                    if ingredients:
                        Ingredient.objects.bulk_create(
                            ingredients,
                            ignore_conflicts=True,
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Loaded {len(ingredients) + skip}"
                                " ingredients."
                            )
                        )
                    if stock_items['isEndOfListReached']:
                        break
                    skip += take
