from django.core.management import BaseCommand

from reports.use_cases.create_feedbacks_report import CreateFeedbacksReport


class Command(BaseCommand):

    def handle(self, *args, **options):
        CreateFeedbacksReport().execute()
        self.stdout.write(
            self.style.SUCCESS('Feedbacks report created successfully.'),
        )
