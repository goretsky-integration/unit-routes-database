from django.core.management import BaseCommand

from accounts.services.crypt import encrypt_string


class Command(BaseCommand):
    help = 'Encrypt string'

    def add_arguments(self, parser):
        parser.add_argument('string', type=str)

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(encrypt_string(options['string']))
        )
