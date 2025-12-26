from django.core.management import BaseCommand

from reports.use_cases.create_birthdays_report import \
    CreateEmployeeBirthdaysReport


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateEmployeeBirthdaysReport().execute()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created employee birthdays report',
            ),
        )
