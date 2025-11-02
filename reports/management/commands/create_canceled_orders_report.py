from django.core.management import BaseCommand

from reports.use_cases.create_canceled_orders_report import \
    CreateCanceledOrdersReportUseCase


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateCanceledOrdersReportUseCase().execute()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created canceled orders report',
            ),
        )
