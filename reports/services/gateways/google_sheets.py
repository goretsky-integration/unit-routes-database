import datetime
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import gspread
from django.conf import settings
from gspread.utils import ValueInputOption

from reports.services.formatters.inventory_stocks import (
    UnitInventoryStocksBalance
)
from reports.services.parsers.canceled_orders import DetailedOrder


def get_canceled_orders_spreadsheet() -> gspread.Spreadsheet:
    client = gspread.service_account(
        filename=settings.GOOGLE_SHEETS_CREDENTIALS,
    )
    return client.open_by_key('11wWpllrZMJnm38Lkb-RuMYySniqH-HWh5d3FKJrzCnI')


def get_inventory_stocks_balance_spreadsheet() -> gspread.Spreadsheet:
    client = gspread.service_account(
        filename=settings.GOOGLE_SHEETS_CREDENTIALS,
    )
    return client.open_by_key('1r2ShKac41c1FG_YDCCimacXhHVU-GNaBi2mOtttPPa4')


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


UNIT_ID_AND_ABBREVIATED_NANE: tuple[tuple[UUID, str], ...] = (
    (UUID('000d3a24-0c71-9a87-11e6-8aba13f80da9'), 'См1'),
    (UUID('000d3a24-0c71-9a87-11e6-8aba13f82835'), 'См2'),
    (UUID('000d3a24-0c71-9a87-11e6-8aba13f88754'), 'См3'),
    (UUID('11f0687c-9f7e-af4c-c4a2-2e455eeb7cd0'), "См5"),
    (uuid4(), "См6"),
    (UUID('000d3a26-b5b0-80f1-11e7-c46eaf0afc18'), "Вязьма-1"),
    (UUID('000d3a24-80c3-810e-11e7-bd751c665f09'), "Под1"),
    (UUID('000d3a39-d824-a82e-11e9-dacc71d4cdf1'), "Под2"),
    (UUID('220ece1a-f30a-9f46-11ed-4958027557a6'), "Под3"),
    (UUID('4e11f854-774d-baec-11ef-047aebf68f29'), "Под4"),
    (UUID('000d3a24-0c71-9a87-11e6-8aba13f9d0ee'), "Обн"),
    (UUID('000d3a23-b0dc-80d9-11e6-b24f4a188a9f'), "М4-1"),
    (UUID('000d3a26-b5b0-80de-11e7-02b7926eda73'), "М4-2"),
    (UUID('2efce17d-4769-9cfb-11ec-f0679180d18b'), "М4-9"),
    (uuid4(), "М4-22"),
    (UUID('000d3a25-8645-a94d-11e8-006460706ab4'), "М4-3"),
    (UUID('000d3a28-4715-a956-11e8-2dcf25c462c3'), "М4-4"),
    (UUID('000d3a25-8645-a954-11e8-333ca08c625f'), "М4-5"),
    (UUID('000d3a28-4715-a958-11e8-333ccf6cf1a0'), "М4-6"),
    (UUID('000d3a22-31e0-a952-11e8-333cdd920305'), "М4-7"),
    (UUID('000d3aac-977b-bb2d-11ec-82bbeeb26721'), "М4-8"),
    (UUID('000d3a21-55a1-80e4-11e7-9a1a1e9c37ac'), "М4-10"),
    (UUID('000d3a25-8645-a954-11e8-333d19605def'), "М4-11"),
    (UUID('000d3a22-31e0-a952-11e8-333d2d4504dd'), "М4-12"),
    (UUID('000d3a21-da51-a812-11e9-40067acb1091'), "М4-16"),
    (UUID('000d3a28-4715-a958-11e8-333d3ee202d9'), "М4-13"),
    (UUID('000d3a29-ff6b-a94b-11e8-f8724c1192bb'), "М4-14"),
    (UUID('000d3a39-d824-a816-11e9-4006175e1abe'), "М4-15"),
    (UUID('000d3a21-da51-a812-11e9-4006b9ffe7fd'), "М4-17"),
    (UUID('000d3a39-d824-a82e-11e9-d84f7dc01968'), "М4-18"),
    (UUID('000d3a39-d824-a82e-11e9-fc73824dc8fd'), "М4-19"),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class InventoryStocksBalanceGoogleSheetsGateway:
    spreadsheet: gspread.Spreadsheet

    def write_data(self, units_balances: Iterable[
        UnitInventoryStocksBalance]) -> None:
        ws = self.spreadsheet.get_worksheet_by_id(1783428251)

        today = datetime.datetime.now(ZoneInfo('Europe/Moscow')).strftime(
            "%d.%m.%Y",
        )
        header_row = ws.row_values(1)

        # If sheet is empty, write first column = abbreviations
        if not header_row:
            ws.update(
                range_name="A1",
                values=[[None], [None]] + [[abbr] for _, abbr in
                                           UNIT_ID_AND_ABBREVIATED_NANE],
            )
            header_row = [None]

        next_col = len(header_row) + 1

        # Write date header
        ws.update_cell(1, next_col, today)

        unit_id_to_balance = {
            unit_balance.unit_id: unit_balance.balance_in_money
            for unit_balance in units_balances
        }

        column_data = []
        for unit_id, _ in UNIT_ID_AND_ABBREVIATED_NANE:
            balance = unit_id_to_balance.get(unit_id)
            column_data.append([balance])

        ws.update(
            range_name=f"{gspread.utils.rowcol_to_a1(3, next_col)}",
            values=column_data,
        )
