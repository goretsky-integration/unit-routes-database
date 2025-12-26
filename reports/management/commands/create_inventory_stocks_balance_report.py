from django.core.management import BaseCommand

from reports.use_cases.create_inventory_stocks_balance_report import \
    CreateInventoryStocksBalanceReportUseCase


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateInventoryStocksBalanceReportUseCase().execute()
