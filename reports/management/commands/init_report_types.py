from django.core.management.base import BaseCommand, CommandError

from reports.models.report_types import ReportType
from reports.selectors import get_report_types

all_report_types = [
    {
        "name": "STATISTICS",
        "verbose_name": "Отчёты по статистике"
    },
    {
        "name": "INGREDIENTS_STOP_SALES",
        "verbose_name": "Стопы (тесто, сыр, пицца-соус)"
    },
    {
        "name": "STREET_STOP_SALES",
        "verbose_name": "Стопы (Улица)"
    },
    {
        "name": "SECTOR_STOP_SALES",
        "verbose_name": "Стопы (Сектор)"
    },
    {
        "name": "PIZZERIA_STOP_SALES",
        "verbose_name": "Стопы (Пиццерия)"
    },
    {
        "name": "STOPS_AND_RESUMES",
        "verbose_name": "Стопы (Остальные ингредиенты)"
    },
    {
        "name": "CANCELED_ORDERS",
        "verbose_name": "Отмены заказов"
    },
    {
        "name": "CHEATED_PHONE_NUMBERS",
        "verbose_name": "Мошенничество с номерами"
    },
    {
        "name": "WRITE_OFFS",
        "verbose_name": "Списания ингредиентов"
    }
]

all_statistics_report_types = [
    {
        "name": "COOKING_TIME",
        "verbose_name": "Время приготовления (общее)"
    },
    {
        "name": "RESTAURANT_COOKING_TIME",
        "verbose_name": "Время приготовления (ресторан)"
    },
    {
        "name": "KITCHEN_PERFORMANCE",
        "verbose_name": "Производительность кухни"
    },
    {
        "name": "DELIVERY_AWAITING_TIME",
        "verbose_name": "Время на полке / 1в1"
    },
    {
        "name": "DELIVERY_SPEED",
        "verbose_name": "Скорость доставки"
    },
    {
        "name": "DELIVERY_PERFORMANCE",
        "verbose_name": "Производительность доставки"
    },
    {
        "name": "BEING_LATE_CERTIFICATES",
        "verbose_name": "Сертификаты за опоздание"
    },
    {
        "name": "DAILY_REVENUE",
        "verbose_name": "Выручка за сегодня"
    },
    {
        "name": "AWAITING_ORDERS",
        "verbose_name": "Остывает на полке"
    },
    {
        "name": "BONUS_SYSTEM",
        "verbose_name": "Бонусная система"
    },
    {
        "name": "PRODUCTIVITY_BALANCE",
        "verbose_name": "Баланс эффективности"
    }
]


class Command(BaseCommand):
    help = 'Init all report types'

    def handle(self, *args, **options):
        report_types_in_database = get_report_types()
        report_type_names_in_database = set(
            report_types_in_database.values_list('name', flat=True)
        )
        report_types_to_insert = [
            ReportType(
                name=report_type['name'],
                verbose_name=report_type['verbose_name'],
            ) for report_type in all_report_types
            if report_type['name'] not in report_type_names_in_database
        ]
        if report_types_to_insert:
            ReportType.objects.bulk_create(report_types_to_insert)

        statistics_report_type = ReportType.objects.get(name='STATISTICS')
        statistics_report_type_names_in_database = set(
            ReportType.objects
            .filter(parent=statistics_report_type)
            .values_list('name', flat=True)
        )
        statistics_report_types_to_insert = [
            ReportType(
                name=report_type['name'],
                verbose_name=report_type['verbose_name'],
                parent=statistics_report_type,
            ) for report_type in all_statistics_report_types
            if report_type['name']
               not in statistics_report_type_names_in_database
        ]
        ReportType.objects.bulk_create(statistics_report_types_to_insert)

        self.stdout.write(self.style.SUCCESS('Done!'))
