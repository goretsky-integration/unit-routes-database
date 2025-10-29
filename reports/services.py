import contextlib
import datetime
import logging
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
    batch_size: ClassVar[Final[int]] = 30
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
                }
            )
            batch_skip += take

            try:
                inventory_stocks_response = InventoryStocksResponse.model_validate_json(
                    response.text
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
        if '(не использовать)' in item.name.lower():
            continue
        if is_all_zero(
            item.average_weekend_expense,
            item.average_weekday_expense,
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


def filter_by_category_names(
        items: Iterable[InventoryStockItem],
        category_names: Iterable[InventoryStockCategoryName],
) -> list[InventoryStockItem]:
    category_names = set(category_names)
    return [
        item for item in items
        if item.category_name in category_names
    ]