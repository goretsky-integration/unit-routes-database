import contextlib
import datetime
import json
from collections.abc import Generator
from dataclasses import dataclass
from typing import NewType, Final, Annotated
from uuid import UUID

import httpx
from pydantic import BaseModel, Field, ValidationError


DodoIsShiftManagerHttpClient = NewType(
    'DodoIsShiftManagerHttpClient', httpx.Client,
)


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


CANCELED_ORDER_STATE_ID: Final[int] = 12


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
