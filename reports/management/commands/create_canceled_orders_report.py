import datetime

from django.core.management import BaseCommand

from reports.use_cases.create_canceled_orders_report import \
    CreateCanceledOrdersReportUseCase


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(),
            help='Date for which to create the canceled orders report (YYYY-MM-DD). '
                 'Defaults to yesterday if not provided.',
            default=datetime.date.today() - datetime.timedelta(days=1),
        )

    def handle(self, *args, **options):
        date = options['date']
        CreateCanceledOrdersReportUseCase(date=date).execute()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created canceled orders report',
            ),
        )
