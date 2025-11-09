from django.core.management import BaseCommand

from reports.use_cases.create_stop_sales_by_new_ingredients_report import \
    CreateStopSalesByNewIngredientsReport


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateStopSalesByNewIngredientsReport().execute()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created stop sales by new ingredients report',
            ),
        )
