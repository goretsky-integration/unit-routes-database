from django.core.management import BaseCommand

from reports.use_cases.create_stop_sales_by_sectors_report import \
    CreateStopSalesBySectorsReport


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateStopSalesBySectorsReport().execute()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created stop sales by sectors report',
            ),
        )
