from django.core.management import BaseCommand

from reports.use_cases.create_stop_sales_by_sales_channels_report import \
    CreateStopSalesBySalesChannelsReport


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateStopSalesBySalesChannelsReport().execute()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created stop sales by sales channels report',
            ),
        )
