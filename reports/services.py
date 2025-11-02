import contextlib
import datetime
import json
import logging
import time
from collections import defaultdict
from collections.abc import Iterable, Generator, Mapping
from dataclasses import dataclass
from enum import StrEnum, auto
from itertools import batched
from typing import Annotated, Any
from typing import NewType, ClassVar, Final
from uuid import UUID

import gspread
import httpx
from django.conf import settings
from django.db.utils import IntegrityError
from gspread.utils import ValueInputOption
from pydantic import BaseModel, Field, ValidationError
from pydantic import computed_field, field_validator

from core.exceptions import AlreadyExistsError
from reports.models.report_routes import ReportRoute
from reports.selectors import (
    get_report_routes,
    filter_report_routes_by_report_type_id,
    filter_report_routes_by_chat_id,
)


logger = logging.getLogger(__name__)


def create_report_routes(
    *,
    telegram_chat_id: int,
    report_type_id: int,
    unit_ids: Iterable[int],
) -> list[ReportRoute]:
    report_routes = [
        ReportRoute(
            unit_id=unit_id,
            telegram_chat_id=telegram_chat_id,
            report_type_id=report_type_id,
        ) for unit_id in unit_ids
    ]
    try:
        return ReportRoute.objects.bulk_create(report_routes)
    except IntegrityError:
        raise AlreadyExistsError('Unit route already exists')


def delete_report_routes(
    *,
    chat_id: int,
    report_type_id: int,
    unit_ids: Iterable[int],
) -> int:
    report_routes = filter_report_routes_by_chat_id(
        queryset=filter_report_routes_by_report_type_id(
            queryset=get_report_routes(),
            report_type_id=report_type_id,
        ),
        chat_id=chat_id,
    ).filter(unit_id__in=unit_ids)
    deleted_rows_count, _ = report_routes.delete()
    return deleted_rows_count


DodoIsApiHttpClient = NewType('DodoIsApiHttpClient', httpx.Client)


@contextlib.contextmanager
def get_dodo_is_api_http_client(
    access_token: str,
    timeout: int = 60,
) -> Generator[DodoIsApiHttpClient, None, None]:
    with httpx.Client(
        headers={
            'Authorization': f'Bearer {access_token}',
        },
        base_url='https://api.dodois.io/dodopizza/ru/',
        timeout=timeout,
    ) as http_client:
        yield DodoIsApiHttpClient(http_client)


class InventoryStockCategoryName(StrEnum):
    INGREDIENT = 'Ingredient'
    SEMI_FINISHED_PRODUCT = 'SemiFinishedProduct'
    FINISHED_PRODUCT = 'FinishedProduct'
    PACKING = 'Packing'


class InventoryStockMeasurementUnit(StrEnum):
    QUANTITY = 'Quantity'
    KILOGRAM = 'Kilogram'
    LITER = 'Liter'
    METER = 'Meter'


class InventoryStockItem(BaseModel):
    id: UUID
    name: str
    unit_id: Annotated[UUID, Field(validation_alias='unitId')]
    category_name: Annotated[
        InventoryStockCategoryName,
        Field(validation_alias='categoryName')
    ]
    quantity: float
    measurement_unit: Annotated[
        InventoryStockMeasurementUnit,
        Field(validation_alias='measurementUnit'),
    ]
    balance_in_money: Annotated[
        float,
        Field(validation_alias='balanceInMoney'),
    ]
    currency: str
    avg_weekday_expense: Annotated[
        float,
        Field(validation_alias='avgWeekdayExpense'),
    ]
    avg_weekend_expense: Annotated[
        float,
        Field(validation_alias='avgWeekendExpense'),
    ]
    days_until_balance_runs_out: Annotated[
        int,
        Field(validation_alias='daysUntilBalanceRunsOut'),
    ]
    calculated_at: Annotated[
        datetime.datetime,
        Field(validation_alias='calculatedAt'),
    ]


class InventoryStocksResponse(BaseModel):
    stocks: list[InventoryStockItem]
    is_end_of_list_reached: Annotated[
        bool,
        Field(validation_alias='isEndOfListReached'),
    ]


def join_unit_ids_with_comma(unit_ids: Iterable[int]) -> str:
    return ','.join(map(str, unit_ids))


@dataclass(frozen=True, slots=True, kw_only=True)
class DodoIsApiGateway:
    batch_size: ClassVar[int] = 30
    http_client: DodoIsApiHttpClient

    def get_inventory_stocks(
        self,
        *,
        unit_ids: Iterable[UUID],
        take: int = 1000,
        skip: int = 0,
    ) -> list[InventoryStockItem]:
        url = '/accounting/inventory-stocks'

        inventory_stocks: list[InventoryStockItem] = []
        for unit_ids_batch in batched(unit_ids, n=self.batch_size):
            batch_skip = skip
            response = self.http_client.get(
                url=url,
                params={
                    'units': join_unit_ids_with_comma(unit_ids_batch),
                    'take': take,
                    'skip': batch_skip,
                },
            )
            batch_skip += take

            try:
                inventory_stocks_response = InventoryStocksResponse.model_validate_json(
                    response.text,
                )
            except ValidationError:
                logger.exception(
                    'Failed to parse inventory stocks response for unit ids: %s',
                    unit_ids_batch,
                )
            else:
                inventory_stocks += inventory_stocks_response.stocks

        return inventory_stocks


@contextlib.contextmanager
def get_dodo_is_api_gateway(
    access_token: str,
    timeout: int = 60,
) -> Generator[DodoIsApiGateway, None, None]:
    with get_dodo_is_api_http_client(
        access_token=access_token,
        timeout=timeout,
    ) as http_client:
        yield DodoIsApiGateway(http_client=http_client)


def is_all_zero(*numbers: int | float) -> bool:
    return all(number == 0 for number in numbers)


def filter_relevant_items(
    items: Iterable[InventoryStockItem],
) -> list[InventoryStockItem]:
    relevant_items: list[InventoryStockItem] = []

    for item in items:
        if 'не использовать' in item.name.lower():
            continue
        if is_all_zero(
            item.avg_weekday_expense,
            item.avg_weekend_expense,
            item.balance_in_money,
            item.quantity,
            item.days_until_balance_runs_out,
        ):
            continue

        relevant_items.append(item)

    return relevant_items


def filter_running_out_stock_items(
    items: Iterable[InventoryStockItem],
    threshold: int,
) -> list[InventoryStockItem]:
    return [
        item for item in items
        if item.days_until_balance_runs_out <= threshold
    ]


@dataclass(frozen=True, slots=True, kw_only=True)
class UnitInventoryStocks:
    unit_id: UUID
    items: list[InventoryStockItem]


def get_empty_units_inventory_stocks(
    unit_ids: Iterable[UUID],
) -> list[UnitInventoryStocks]:
    return [
        UnitInventoryStocks(
            unit_id=unit_id,
            items=[],
        )
        for unit_id in unit_ids
    ]


def group_inventory_stocks(
    items: Iterable[InventoryStockItem],
) -> list[UnitInventoryStocks]:
    unit_id_to_items: dict[UUID, list[InventoryStockItem]] = defaultdict(list)
    for item in items:
        unit_id_to_items[item.unit_id].append(item)
    return [
        UnitInventoryStocks(
            unit_id=unit_id,
            items=items,
        )
        for unit_id, items in unit_id_to_items.items()
    ]


MEASUREMENT_UNIT_TO_NAME = {
    InventoryStockMeasurementUnit.KILOGRAM: 'кг',
    InventoryStockMeasurementUnit.LITER: 'л',
    InventoryStockMeasurementUnit.METER: 'м',
    InventoryStockMeasurementUnit.QUANTITY: 'шт',
}


def format_running_out_stock_items(
    unit_name: str,
    items: Iterable[InventoryStockItem],
) -> str:
    items = list(items)

    lines: list[str] = [f'<b>{unit_name}</b>']

    if items:
        lines.append('<b>❗️ На сегодня не хватит ❗️</b>')
    else:
        lines.append('<b>На сегодня всего достаточно</b>')

    items.sort(key=lambda item: item.name)

    for item in items:
        measurement_unit_name = MEASUREMENT_UNIT_TO_NAME.get(
            item.measurement_unit,
            item.measurement_unit,
        )
        lines.append(
            f'📍 {item.name}'
            f' - остаток <b><u>{item.quantity} {measurement_unit_name}</u></b>',
        )

    return '\n'.join(lines)


DodoIsShiftManagerHttpClient = NewType(
    'DodoIsShiftManagerHttpClient', httpx.Client,
)

CANCELED_ORDER_STATE_ID: Final[int] = 12


@contextlib.contextmanager
def get_dodo_is_shift_manager_http_client(
) -> Generator[DodoIsShiftManagerHttpClient, None, None]:
    base_url = f'https://shiftmanager.dodopizza.ru/'
    headers = {'User-Agent': 'Goretsky-Band'}

    with httpx.Client(
        headers=headers,
        base_url=base_url,
        follow_redirects=True,
    ) as http_client:
        yield DodoIsShiftManagerHttpClient(http_client)


def build_partial_orders_request_payload(
    *,
    date: datetime.date,
    page: int = 1,
    per_page: int = 100,
) -> dict[str, str | int]:
    query_params = {
        'date': f'{date:%Y-%m-%d}',
        'perPage': per_page,
        'page': page,
        'state': CANCELED_ORDER_STATE_ID,
    }
    return query_params


@dataclass(frozen=True, slots=True, kw_only=True)
class DodoIsShiftManagerGateway:
    http_client: DodoIsShiftManagerHttpClient

    def get_partial_orders(
        self,
        *,
        cookies: dict[str, str],
        date: datetime.date,
        page: int = 1,
        per_page: int = 100,
    ) -> httpx.Response:
        """
        Retrieve partial orders from Dodo IS.

        Keyword Args:
            cookies: Cookies to be sent with the request.
            date: Date of orders to retrieve.
            page: Page number.
            per_page: Number of orders per page.

        Returns:
            httpx.Response object.
        """
        url = '/api/orders'
        query_params = build_partial_orders_request_payload(
            date=date,
            page=page,
            per_page=per_page,
        )
        response = self.http_client.get(
            url=url,
            params=query_params,
            cookies=cookies,
        )
        return response

    def get_detailed_order(
        self,
        *,
        cookies: dict[str, str],
        order_id: UUID,
    ) -> httpx.Response:
        url = f'/api/orders/{order_id.hex.upper()}'
        response = self.http_client.get(url=url, cookies=cookies)
        return response


class PartialOrder(BaseModel):
    id: Annotated[UUID, Field(alias='Id')]


class PartialOrdersResponsePagination(BaseModel):
    current_page: Annotated[int, Field(alias='CurrentPage')]
    next_page: Annotated[int | None, Field(alias='NextPage')]
    per_page: Annotated[int, Field(alias='PerPage')]
    prev_page: Annotated[int | None, Field(alias='PrevPage')]
    total_pages: Annotated[int, Field(alias='TotalPages')]
    total_records: Annotated[int, Field(alias='TotalRecords')]


class PartialOrdersResponse(BaseModel):
    items: Annotated[list[PartialOrder], Field(alias='Items')]
    pagination: Annotated[
        PartialOrdersResponsePagination,
        Field(alias='Pagination'),
    ]


def parse_partial_orders_response(
    response: httpx.Response,
) -> PartialOrdersResponse:
    try:
        response_data = response.json()
        partial_orders_response = PartialOrdersResponse.model_validate(
            response_data,
        )
    except (json.JSONDecodeError, ValidationError) as error:
        raise

    return partial_orders_response


class CountryCode(StrEnum):
    RU = auto()


class SalesChannel(StrEnum):
    DELIVERY = auto()
    DINE_IN = auto()


class DetailedOrderDelivery(BaseModel):
    courier: Annotated[Any | None, Field(validation_alias='Courier')]

    @computed_field
    @property
    def is_courier_assigned(self) -> bool:
        return self.courier is not None


class DetailedOrderPayment(BaseModel):
    price: Annotated[int, Field(validation_alias='Price')]


class DetailedOrderHistoryItem(BaseModel):
    date: Annotated[datetime.datetime, Field(validation_alias='Date')]
    description: Annotated[str, Field(validation_alias='Description')]
    user_name: Annotated[str | None, Field(validation_alias='UserName')]

    @field_validator('user_name', mode='before')
    @classmethod
    def empty_string_to_none(cls, value: str) -> str | None:
        return None if value == '' else value


class DetailedOrderClient(BaseModel):
    phone: Annotated[str | None, Field(validation_alias='Phone')]


class DetailedOrder(BaseModel):
    id: Annotated[UUID, Field(validation_alias='Id')]
    account_name: str
    courier_needed: Annotated[bool, Field(validation_alias='CourierNeeded')]
    history: Annotated[
        list[DetailedOrderHistoryItem],
        Field(validation_alias='History'),
    ]
    number: Annotated[str, Field(validation_alias='Number')]
    payment: Annotated[DetailedOrderPayment, Field(validation_alias='Payment')]
    delivery: Annotated[
        DetailedOrderDelivery,
        Field(validation_alias='Delivery'),
    ]
    client: Annotated[DetailedOrderClient, Field(validation_alias='Client')]

    @property
    def created_at(self) -> datetime.datetime | None:
        date: datetime.datetime | None = None
        for item in self.history:
            if date is None or item.date < date:
                date = item.date
        return date

    @computed_field
    @property
    def sales_channel(self) -> SalesChannel:
        return (
            SalesChannel.DELIVERY if self.courier_needed
            else SalesChannel.DINE_IN
        )

    @computed_field
    @property
    def is_refund_receipt_printed(self) -> bool:
        for item in self.history:
            if 'закрыт чек на возврат' in item.description.lower():
                return True
        return False

    @computed_field
    @property
    def is_canceled_by_employee(self) -> bool:
        for item in self.history:
            is_order_canceled_item = (
                'has been rejected' in item.description.lower()
            )
            has_user_name = item.user_name is not None
            if is_order_canceled_item and has_user_name:
                return True

        return False


def filter_valid_canceled_orders(
    orders: Iterable[DetailedOrder],
) -> list[DetailedOrder]:
    result: list[DetailedOrder] = []
    for order in orders:
        if order.sales_channel == SalesChannel.DINE_IN and order.is_canceled_by_employee:
            result.append(order)
        if order.sales_channel == SalesChannel.DELIVERY and order.delivery.is_courier_assigned:
            result.append(order)
    return result


def parse_detailed_order_response(
    response: httpx.Response,
    account_name: str,
) -> DetailedOrder:
    try:
        response_data = response.json()
        response_data |= {'account_name': account_name}
        return DetailedOrder.model_validate(response_data)
    except (json.JSONDecodeError, ValidationError) as error:
        raise


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


def get_canceled_orders_spreadsheet() -> gspread.Spreadsheet:
    client = gspread.service_account(
        filename=settings.GOOGLE_SHEETS_CREDENTIALS,
    )
    return client.open_by_key('11wWpllrZMJnm38Lkb-RuMYySniqH-HWh5d3FKJrzCnI')


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
