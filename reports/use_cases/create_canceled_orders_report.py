import datetime
import logging
from dataclasses import dataclass

from accounts.models import AccountCookies
from accounts.services.crypt import decrypt_dict
from reports.services.filters.canceled_orders import (
    filter_valid_canceled_orders,
)
from reports.services.gateways.google_sheets import (
    get_canceled_orders_spreadsheet,
    CanceledOrdersGoogleSheetsGateway,
)
from reports.services.gateways.shift_manager import (
    get_dodo_is_shift_manager_http_client,
    DodoIsShiftManagerGateway,
    parse_partial_orders_response,
)
from reports.services.parsers.canceled_orders import (
    parse_detailed_order_response,
)
from units.models import Unit


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCanceledOrdersReportUseCase:
    date: datetime.date

    def execute(self) -> None:
        accounts_cookies = (
            AccountCookies.objects
            .filter(name__startswith='shift_')
            .select_related('account')
        )
        units = Unit.objects.all()
        account_name_to_cookies = {
            account_cookies.name: account_cookies.encrypted_cookies
            for account_cookies in accounts_cookies
        }
        spreadsheet = get_canceled_orders_spreadsheet()
        worksheets = spreadsheet.worksheets(exclude_hidden=True)
        google_sheets_gateway = CanceledOrdersGoogleSheetsGateway(
            worksheets=worksheets,
            account_name_to_unit_name={
                unit.shift_manager_account_name: unit.name
                for unit in units
            },
        )

        with get_dodo_is_shift_manager_http_client() as http_client:
            for unit in units:
                if unit.shift_manager_account_name not in account_name_to_cookies:
                    logger.warning(
                        'No cookies found for unit %s with account name %s',
                        unit.name,
                        unit.shift_manager_account_name,
                    )
                    continue
                encrypted_cookies = account_name_to_cookies[
                    unit.shift_manager_account_name]
                cookies = decrypt_dict(encrypted_cookies)

                gateway = DodoIsShiftManagerGateway(
                    http_client=http_client,
                )
                orders_response = gateway.get_partial_orders(
                    cookies=cookies, date=self.date,
                )

                partial_orders = parse_partial_orders_response(orders_response)

                detailed_orders = []
                for order in partial_orders.items:
                    detailed_order_response = gateway.get_detailed_order(
                        cookies=cookies,
                        order_id=order.id,
                    )
                    detailed_order = parse_detailed_order_response(
                        response=
                        detailed_order_response,
                        account_name=unit.shift_manager_account_name,
                    )
                    detailed_orders.append(detailed_order)

                detailed_orders = filter_valid_canceled_orders(detailed_orders)

                for order in detailed_orders:
                    google_sheets_gateway.append_order(order)
