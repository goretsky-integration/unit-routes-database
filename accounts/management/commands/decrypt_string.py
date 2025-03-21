from cryptography.fernet import InvalidToken
from django.core.management import BaseCommand

from accounts.services.crypt import decrypt_string


class Command(BaseCommand):
    help = 'Decrypt string'

    def add_arguments(self, parser):
        parser.add_argument('string', type=str)

    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS(decrypt_string(options['string']))
            )
        except InvalidToken:
            self.stdout.write(
                self.style.ERROR('Invalid token')
           )
