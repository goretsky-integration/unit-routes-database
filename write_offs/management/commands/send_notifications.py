from django.core.management import BaseCommand
from django.db.models import QuerySet

from reports.models.report_routes import ReportRoute
from write_offs.models import IngredientWriteOff
from write_offs.services import (
    get_expired_repeating_write_offs,
    get_upcoming_write_offs,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        write_offs: QuerySet[IngredientWriteOff] = (
                get_upcoming_write_offs()
                + get_expired_repeating_write_offs()
        )

        for write_off in write_offs:
            chat_ids = ReportRoute.objects.filter(unit_id=write_off.unit_id).values_list('telegram_chat__chat_id', flat=True)

            for chat_id in chat_ids:

