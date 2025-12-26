from django.core.management import BaseCommand

from reports.use_cases.create_stop_sales_by_all_ingredients_report import \
    CreateStopSalesByAllIngredientsReport


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateStopSalesByAllIngredientsReport().execute()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created stop sales by all ingredients report',
            ),
        )
