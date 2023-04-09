import json

from django.conf import settings
from django.core.management.base import BaseCommand

from reports.models.report_types import ReportType
from reports.selectors import get_report_types


class Command(BaseCommand):
    help = 'Init all report types'

    def handle(self, *args, **options):
        report_types_file_path = (
                settings.BASE_DIR / 'report_types.json'
        )
        all_report_types: list[dict] = json.loads(
            report_types_file_path.read_text()
        )

        statistics_report_types_file_path = (
                settings.BASE_DIR / 'statistics_report_types.json'
        )
        all_statistics_report_types: list[dict] = json.loads(
            statistics_report_types_file_path.read_text()
        )

        report_type_names_in_database = set(
            ReportType.objects.values_list('name', flat=True)
        )

        for report_type in all_report_types:
            if report_type['name'] in report_type_names_in_database:
                self.stdout.write(
                    self.style.WARNING(
                        f'Report type {report_type["name"]} already exists',
                    )
                )
                continue

            ReportType.objects.create(
                name=report_type['name'],
                verbose_name=report_type['verbose_name'],
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Report type {report_type["name"]} created',
                )
            )

        statistics_report_type = ReportType.objects.get(name='STATISTICS')

        statistics_report_type_names_in_database = set(
            ReportType.objects
            .filter(parent=statistics_report_type)
            .values_list('name', flat=True)
        )

        for report_type in all_statistics_report_types:
            if report_type['name'] in statistics_report_type_names_in_database:
                self.stdout.write(
                    self.style.WARNING(
                        f'Statistics report type {report_type["name"]}'
                        ' already exists',
                    )
                )
                continue

            ReportType.objects.create(
                name=report_type['name'],
                verbose_name=['verbose_name'],
                parent=statistics_report_type,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Statistics report type {report_type["name"]} created',
                )
            )
