from django.core.management import BaseCommand

from snapshots.use_cases.download_inventory_stocks import \
    DownloadInventoryStocksUseCase


class Command(BaseCommand):

    def handle(self, *args, **options):
        use_case = DownloadInventoryStocksUseCase()
        use_case.execute()
