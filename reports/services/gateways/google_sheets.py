import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

import gspread
from django.conf import settings
from gspread.utils import ValueInputOption

from reports.services.parsers.canceled_orders import DetailedOrder


def get_canceled_orders_spreadsheet() -> gspread.Spreadsheet:
    client = gspread.service_account(
        filename=settings.GOOGLE_SHEETS_CREDENTIALS,
    )
    return client.open_by_key('11wWpllrZMJnm38Lkb-RuMYySniqH-HWh5d3FKJrzCnI')


UNIT_NAME_TO_ABBREVIATION = {
    'Подольск-3': 'П-3',
    'Подольск-2': 'П-2',
    'Подольск-1': 'П-1',
    'Подольск-4': 'П-4',
    'Москва 4-16': '4-16',
    'Москва 4-9': '4-9',
    'Москва 4-8': '4-8',
    'Москва 4-19': '4-19',
    'Москва 4-18': '4-18',
    'Москва 4-17': '4-17',
    'Москва 4-15': '4-15',
    'Москва 4-14': '4-14',
    'Москва 4-13': '4-13',
    'Москва 4-12': '4-12',
    'Москва 4-11': '4-11',
    'Москва 4-7': '4-7',
    'Москва 4-6': '4-6',
    'Москва 4-5': '4-5',
    'Москва 4-4': '4-4',
    'Москва 4-3': '4-3',
    'Москва 4-10': '4-10',
    'Москва 4-2': '4-2',
    'Москва 4-1': '4-1',
    'Смоленск-1': 'С-1',
    'Смоленск-2': 'С-2',
    'Смоленск-3': 'С-3',
    'Смоленск-4': 'С-4',
    'Смоленск-5': 'С-5',
    'Вязьма-1': 'В-1',
    'Обнинск-1': 'О-1',
}


@dataclass(frozen=True, slots=True, kw_only=True)
class CanceledOrdersGoogleSheetsGateway:
    worksheets: Iterable[gspread.Worksheet]
    account_name_to_unit_name: Mapping[str, str]

    def append_order(self, order: DetailedOrder) -> None:
        try:
            unit_name = self.account_name_to_unit_name[order.account_name]
        except KeyError:
            return

        abbreviation = UNIT_NAME_TO_ABBREVIATION.get(unit_name, unit_name)

        title_to_worksheet = {
            worksheet.title: worksheet
            for worksheet in self.worksheets
        }

        if abbreviation not in title_to_worksheet:
            return

        order_url = f'=HYPERLINK("https://shiftmanager.dodopizza.ru/Managment/ShiftManagment/Orders#/order/{order.id.hex.upper()}"; "{order.number}")'
        worksheet = title_to_worksheet[abbreviation]
        worksheet.append_row(
            [
                f'{order.created_at:%d.%m.%Y}',
                'Доставка' if order.courier_needed else 'Ресторан',
                order_url,
                order.payment.price,
                order.client.phone,
            ],
            value_input_option=ValueInputOption.user_entered,
        )
        time.sleep(2.5)
