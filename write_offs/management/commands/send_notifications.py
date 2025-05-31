from django.core.management import BaseCommand

from write_offs.services import (
    get_expired_repeating_write_offs,
    get_upcoming_write_offs,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        write_offs = get_upcoming_write_offs() + get_expired_repeating_write_offs()

