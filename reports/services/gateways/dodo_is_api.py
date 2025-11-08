import contextlib
import datetime
import logging
from collections.abc import Generator
from dataclasses import dataclass
from enum import StrEnum
from itertools import batched
from typing import ClassVar, Iterable, NewType, Annotated
from uuid import UUID

import httpx
from pydantic import ValidationError, Field, BaseModel


logger = logging.getLogger(__name__)

DodoIsApiHttpClient = NewType('DodoIsApiHttpClient', httpx.Client)


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


def join_unit_ids_with_comma(unit_ids: Iterable[UUID]) -> str:
    return ','.join(map(str, unit_ids))


class StaffMemberBirthday(BaseModel):
    staff_id: Annotated[UUID, Field(validation_alias='staffId')]
    first_name: Annotated[str, Field(validation_alias='firstName')]
    last_name: Annotated[str, Field(validation_alias='lastName')]
    date_of_birth: Annotated[
        datetime.date,
        Field(validation_alias='dateOfBirth'),
    ]
    unit_id: Annotated[UUID, Field(validation_alias='unitId')]
    unit_name: Annotated[str, Field(validation_alias='unitName')]


class StaffMembersBirthdaysResponse(BaseModel):
    birthdays: list[StaffMemberBirthday]
    is_end_of_list_reached: Annotated[
        bool,
        Field(validation_alias='isEndOfListReached'),
    ]


class SalesChannel(StrEnum):
    DINE_IN = 'Dine-in'
    TAKEAWAY = 'Takeaway'
    DELIVERY = 'Delivery'


class ChannelStopType(StrEnum):
    COMPLETE = 'Complete'
    REDIRECTION = 'Redirection'


class StopSaleBySalesChannel(BaseModel):
    id: UUID
    unit_id: Annotated[UUID, Field(validation_alias='unitId')]
    unit_name: Annotated[str, Field(validation_alias='unitName')]
    sales_channel: Annotated[
        SalesChannel,
        Field(validation_alias='salesChannel'),
    ]
    reason: str
    started_at_local: Annotated[
        datetime.datetime,
        Field(validation_alias='startedAtLocal'),
    ]
    ended_at_local: Annotated[
        datetime.datetime | None,
        Field(validation_alias='endedAtLocal'),
    ]
    stopped_by_user_id: Annotated[
        UUID,
        Field(validation_alias='stoppedByUserId'),
    ]
    resumed_by_user_id: Annotated[
        UUID | None,
        Field(validation_alias='resumedByUserId'),
    ]
    channel_stop_type: Annotated[
        ChannelStopType,
        Field(validation_alias='channelStopType'),
    ]


class StopSalesBySalesChannelsResponse(BaseModel):
    stop_sales: Annotated[
        list[StopSaleBySalesChannel],
        Field(validation_alias='stopSalesBySalesChannels'),
    ]


class IngredientCategoryName(StrEnum):
    INGREDIENT = 'Ingredient'
    SEMI_FINISHED_PRODUCT = 'SemiFinishedProduct'
    FINISHED_PRODUCT = 'FinishedProduct'
    INVENTORY = 'Inventory'
    PACKING = 'Packing'
    CONSUMABLES = 'Consumables'


class StopSaleByIngredient(BaseModel):
    id: UUID
    unit_id: Annotated[UUID, Field(validation_alias='unitId')]
    unit_name: Annotated[str, Field(validation_alias='unitName')]
    ingredient_id: Annotated[UUID, Field(validation_alias='ingredientId')]
    ingredient_name: Annotated[str, Field(validation_alias='ingredientName')]
    ingredient_category_name: Annotated[
        IngredientCategoryName,
        Field(validation_alias='ingredientCategoryName'),
    ]
    reason: str
    started_at_local: Annotated[
        datetime.datetime,
        Field(validation_alias='startedAtLocal'),
    ]
    ended_at_local: Annotated[
        datetime.datetime | None,
        Field(validation_alias='endedAtLocal'),
    ]
    stopped_by_user_id: Annotated[
        UUID,
        Field(validation_alias='stoppedByUserId'),
    ]
    resumed_by_user_id: Annotated[
        UUID | None,
        Field(validation_alias='resumedByUserId'),
    ]


class StopSalesByIngredientsResponse(BaseModel):
    stop_sales: Annotated[
        list[StopSaleByIngredient],
        Field(validation_alias='stopSalesByIngredients'),
    ]


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


@dataclass(frozen=True, slots=True, kw_only=True)
class DodoIsApiGateway:
    batch_size: ClassVar[int] = 30
    http_client: DodoIsApiHttpClient

    def get_batched_units(
        self,
        unit_ids: Iterable[UUID],
    ) -> list[tuple[UUID, ...]]:
        return list(batched(unit_ids, n=self.batch_size))

    def get_stop_sales_by_ingredients(
        self,
        *,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
        unit_ids: Iterable[UUID],
    ) -> list[StopSaleByIngredient]:
        url = '/production/stop-sales-ingredients'
        stop_sales: list[StopSaleByIngredient] = []

        for unit_ids_batch in self.get_batched_units(unit_ids=unit_ids):
            response = self._try_send_request_with_server_error_handling(
                url=url,
                params={
                    'units': join_unit_ids_with_comma(unit_ids_batch),
                    'from': f'{date_from:%Y-%m-%dT%H:%M:%S}',
                    'to': f'{date_to:%Y-%m-%dT%H:%M:%S}',
                },
            )
            if response is None:
                logger.error(
                    'Failed to get stop sales by ingredients for units %s. No response.',
                    unit_ids_batch,
                )
                break

            try:
                stop_sales_response = StopSalesByIngredientsResponse.model_validate_json(
                    response.text,
                )
            except ValidationError:
                logger.exception(
                    "Failed to parse stop sales by ingredients response for unit ids: %s",
                    unit_ids_batch,
                )
                break
            else:
                stop_sales.extend(stop_sales_response.stop_sales)

        return stop_sales

    def get_stop_sales_by_sales_channels(
        self,
        *,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
        unit_ids: Iterable[UUID],
    ) -> list[StopSaleBySalesChannel]:
        url = '/production/stop-sales-channels'
        stop_sales: list[StopSaleBySalesChannel] = []

        for unit_ids_batch in self.get_batched_units(unit_ids=unit_ids):
            response = self._try_send_request_with_server_error_handling(
                url=url,
                params={
                    'units': join_unit_ids_with_comma(unit_ids_batch),
                    'from': f'{date_from:%Y-%m-%dT%H:%M:%S}',
                    'to': f'{date_to:%Y-%m-%dT%H:%M:%S}',
                },
            )
            if response is None:
                logger.error(
                    'Failed to get stop sales by sales channels for units %s. No response.',
                    unit_ids_batch,
                )
                break

            try:
                stop_sales_response = StopSalesBySalesChannelsResponse.model_validate_json(
                    response.text,
                )
            except ValidationError:
                logger.exception(
                    "Failed to parse stop sales by sales channels response for unit ids: %s",
                    unit_ids_batch,
                )
                break
            else:
                stop_sales.extend(stop_sales_response.stop_sales)

        return stop_sales

    def get_staff_members_birthdays(
        self,
        *,
        day_from: int,
        day_to: int,
        month_from: int,
        month_to: int,
        unit_ids: Iterable[UUID],
    ) -> list[StaffMemberBirthday]:
        url = '/staff/members/birthdays'
        staff_birthdays: list[StaffMemberBirthday] = []
        take: int = 100

        for unit_ids_batch in self.get_batched_units(unit_ids=unit_ids):
            for skip in range(0, 100_000, take):
                response = self._try_send_request_with_server_error_handling(
                    url=url,
                    params={
                        'units': join_unit_ids_with_comma(unit_ids_batch),
                        'dayFrom': day_from,
                        'dayTo': day_to,
                        'monthFrom': month_from,
                        'monthTo': month_to,
                        'take': take,
                        'skip': skip,
                    },
                )
                if response is None:
                    logger.error(
                        'Failed to get staff members for units %s. No response.',
                        unit_ids_batch,
                    )
                    break

                try:
                    birthdays_response = StaffMembersBirthdaysResponse.model_validate_json(
                        response.text,
                    )
                except ValidationError:
                    logger.exception(
                        "Failed to parse birthdays response for unit ids: %s",
                        unit_ids_batch,
                    )
                    break
                else:
                    staff_birthdays.extend(birthdays_response.birthdays)
                    if birthdays_response.is_end_of_list_reached:
                        break

        return staff_birthdays

    def _try_send_request_with_server_error_handling(
        self,
        url: str,
        params: dict[str, str | int],
        max_retries: int = 5,
    ) -> httpx.Response | None:
        for attempt in range(1, max_retries + 1):
            response = self.http_client.get(url=url, params=params)

            if response.is_server_error:
                logger.warning(
                    "Server error (%s) on attempt %d/%d for params",
                    response.status_code,
                    attempt,
                    max_retries,
                    params,
                )
                if attempt < max_retries:
                    continue
                else:
                    logger.error("Max retries reached")
                    break

            return response

        return None

    def get_inventory_stocks(
        self,
        *,
        unit_ids: Iterable[UUID],
    ) -> list[InventoryStockItem]:
        take: int = 1000
        url = '/accounting/inventory-stocks'
        inventory_stocks: list[InventoryStockItem] = []

        for unit_ids_batch in batched(unit_ids, n=self.batch_size):
            for skip in range(0, 100_000, take):
                response = self._try_send_request_with_server_error_handling(
                    url=url,
                    params={
                        'units': join_unit_ids_with_comma(unit_ids_batch),
                        'take': take,
                        'skip': skip,
                    },
                )

                if response is None:
                    logger.error(
                        'Failed to get inventory stocks for units %s. No response.',
                        unit_ids_batch,
                    )
                    break

                try:
                    inventory_stocks_response = InventoryStocksResponse.model_validate_json(
                        response.text,
                    )
                except ValidationError:
                    logger.exception(
                        "Failed to parse inventory stocks response for unit ids: %s",
                        unit_ids_batch,
                    )
                    break
                else:
                    inventory_stocks += inventory_stocks_response.stocks
                    if inventory_stocks_response.is_end_of_list_reached:
                        break

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
