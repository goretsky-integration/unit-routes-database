import json

from django.core.management.base import BaseCommand
from django.conf import settings

from accounts.models import AccountRole


class Command(BaseCommand):
    help = 'Init all account roles'

    def handle(self, *args, **options):
        account_roles_file_path = settings.BASE_DIR / 'account_roles.json'
        account_roles = json.loads(account_roles_file_path.read_text())

        account_roles_in_database = AccountRole.objects.values('id', 'name')
        account_role_ids_in_database = {
            role['id'] for role in account_roles_in_database
        }
        account_role_names_in_database = {
            role['name'] for role in account_roles_in_database
        }

        for account_role in account_roles:
            account_role_id = account_role['id']
            account_role_name = account_role['name']

            if account_role_id in account_role_ids_in_database:
                self.stdout.write(
                    self.style.WARNING(
                        f'Role with ID {account_role_id} already exists'
                    )
                )
                continue
            if account_role_name in account_role_names_in_database:
                self.stdout.write(
                    self.style.WARNING(
                        f'Role with name {account_role_name} already exists'
                    )
                )
                continue

            AccountRole.objects.create(
                id=account_role_id,
                name=account_role_name,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Account ID {account_role_id}'
                    f' name {account_role_name} created'
                )
            )
