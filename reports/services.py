import contextlib
import datetime
import logging
from collections import defaultdict
from collections.abc import Iterable, Generator
from dataclasses import dataclass
from enum import StrEnum
from itertools import batched
from typing import NewType, ClassVar, Final, Annotated
from uuid import UUID

import httpx
from django.db.utils import IntegrityError
from pydantic import BaseModel, Field, ValidationError

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
