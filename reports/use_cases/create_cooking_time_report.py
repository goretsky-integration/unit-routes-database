from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from accounts.services.crypt import decrypt_string
from reports.services.formatters.delivery import (
    format_restaurant_cooking_time_report, format_delivery_cooking_time_report,
)
from reports.services.gateways.dodo_is_api import (
    get_dodo_is_api_gateway,
    OrdersHandoverStatisticsRequestParamSalesChannel,
    UnitOrdersHandoverStatistics,
)
from reports.services.period import Period
from reports.use_cases.create_report import CreateReportUseCase
from telegram.services import batch_create_telegram_messages
from units.models import Unit


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCookingTimeReportUseCase(CreateReportUseCase):
    timezone: ZoneInfo = ZoneInfo("Europe/Moscow")

    @abstractmethod
    def get_sales_channels(self) -> list[
        OrdersHandoverStatisticsRequestParamSalesChannel]:
        pass

    @abstractmethod
    def format_report(
        self,
        units: Iterable[Unit],
        units_statistics: Iterable[UnitOrdersHandoverStatistics],
    ) -> str:
        pass

    def execute(self) -> None:
        today = Period.today_to_this_time(self.timezone)
        all_units = []
        result = []
        for account_token, units in self.get_account_tokens_and_units():
            all_units += units
            access_token = decrypt_string(account_token.encrypted_access_token)

            with get_dodo_is_api_gateway(
                access_token=access_token,
            ) as dodo_is_api_gateway:
                result += dodo_is_api_gateway.get_orders_handover_statistics(
                    date_from=today.start,
                    date_to=today.end,
                    unit_ids={unit.uuid for unit in units},
                    sales_channels=self.get_sales_channels(),
                )

        text = self.format_report(all_units, result)
        batch_create_telegram_messages(
            chat_ids=[self.chat_id],
            text=text,
        )


class CreateRestaurantCookingTimeReportUseCase(CreateCookingTimeReportUseCase):
    def get_sales_channels(self) -> list[
        OrdersHandoverStatisticsRequestParamSalesChannel]:
        return [OrdersHandoverStatisticsRequestParamSalesChannel.DINE_IN]

    def format_report(
        self,
        units: Iterable[Unit],
        units_statistics: Iterable[UnitOrdersHandoverStatistics],
    ) -> str:
        return format_restaurant_cooking_time_report(units, units_statistics)


class CreateDeliveryCookingTimeReportUseCase(CreateCookingTimeReportUseCase):
    def get_sales_channels(self) -> list[
        OrdersHandoverStatisticsRequestParamSalesChannel]:
        return [OrdersHandoverStatisticsRequestParamSalesChannel.DELIVERY]

    def format_report(
        self,
        units: Iterable[Unit],
        units_statistics: Iterable[UnitOrdersHandoverStatistics],
    ) -> str:
        return format_delivery_cooking_time_report(units, units_statistics)
