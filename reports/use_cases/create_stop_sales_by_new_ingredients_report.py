from collections.abc import Iterable
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from redis import Redis

from accounts.models import AccountTokens
from accounts.services.crypt import decrypt_string
from core.services import get_redis
from reports.models.report_routes import ReportRoute
from reports.services.filters.stop_sales import filter_not_ended_stop_sales
from reports.services.formatters.stop_sales import (
    group_by_unit_id,
    format_stop_sales_by_ingredients, group_by_reason,
    StopSalesGroupedByUnitId,
)
from reports.services.gateways.dodo_is_api import (
    get_dodo_is_api_gateway,
    StopSaleByIngredient,
)
from reports.services.period import Period
from telegram.services import batch_create_telegram_messages
from units.models import Unit


class NewStopSalesFilter:

    def __init__(self, redis: Redis):
        self.__redis = redis

    def filter(
        self,
        stop_sales: Iterable[StopSaleByIngredient],
    ) -> list[StopSaleByIngredient]:
        new_stop_sales = []
        for stop_sale in stop_sales:
            redis_key = (
                f'stop-sales:new-ingredients:{stop_sale.id.hex}'
            )
            if not self.__redis.exists(redis_key):
                new_stop_sales.append(stop_sale)
                self.__redis.set(redis_key, '1', ex=3 * 24 * 60 * 60)
        return new_stop_sales


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateStopSalesByNewIngredientsReport:
    timezone = ZoneInfo('Europe/Moscow')

    def execute(self) -> None:
        accounts_tokens = AccountTokens.objects.select_related('account').all()
        today = Period.today_to_this_time(self.timezone)

        new_stop_sales_filter = NewStopSalesFilter(get_redis())

        for account_token in accounts_tokens:
            units = Unit.objects.filter(
                dodo_is_api_account_name=account_token.account.name,
            )
            unit_ids = {unit.uuid for unit in units}
            unit_id_to_name = {unit.uuid: unit.name for unit in units}

            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                stop_sales = dodo_is_api_gateway.get_stop_sales_by_ingredients(
                    unit_ids=unit_ids,
                    date_from=today.start,
                    date_to=today.end,
                )

            stop_sales = filter_not_ended_stop_sales(stop_sales)
            stop_sales = new_stop_sales_filter.filter(stop_sales)

            existing_stop_sales_unit_ids = {stop_sale.unit_id for stop_sale in stop_sales}
            missing_unit_ids = unit_ids - existing_stop_sales_unit_ids
            missing_stop_sales = [
                StopSalesGroupedByUnitId(
                    unit_id=unit_id,
                    stop_sales=[],
                )
                for unit_id in missing_unit_ids
            ]

            units_stop_sales = group_by_unit_id(stop_sales) + missing_stop_sales

            for unit_stop_sales in units_stop_sales:
                unit_name = unit_id_to_name.get(unit_stop_sales.unit_id, '?')
                text = format_stop_sales_by_ingredients(
                    unit_name=unit_name,
                    stop_sales_by_reasons=group_by_reason(
                        unit_stop_sales.stop_sales,
                    ),
                )

                chat_ids = (
                    ReportRoute.objects
                    .filter(
                        report_type__name='INGREDIENTS_STOP_SALES',
                        unit__uuid=unit_stop_sales.unit_id,
                    )
                    .values_list('telegram_chat__chat_id', flat=True)
                )
                batch_create_telegram_messages(
                    chat_ids=chat_ids,
                    text=text,
                )
