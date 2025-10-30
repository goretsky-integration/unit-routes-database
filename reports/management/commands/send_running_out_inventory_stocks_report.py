from django.core.management import BaseCommand

from reports.use_cases.create_running_out_inventory_stocks_report import (
    CreateRunningOutInventoryStocksReportUseCase,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateRunningOutInventoryStocksReportUseCase().execute()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully sent running out inventory stocks report',
            ),
        )
