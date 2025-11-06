import datetime
import json
from enum import StrEnum, auto
from typing import Any, Annotated
from uuid import UUID

import httpx
from pydantic import (
    computed_field,
    BaseModel,
    Field,
    field_validator,
    ValidationError,
)


class SalesChannel(StrEnum):
    DELIVERY = auto()
    DINE_IN = auto()
    TAKEAWAY = auto()


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


def parse_detailed_order_response(
    response: httpx.Response,
    account_name: str,
) -> DetailedOrder:
    try:
        response_data = response.json()
        response_data |= {'account_name': account_name}
        return DetailedOrder.model_validate(response_data)
    except (json.JSONDecodeError, ValidationError):
        raise
