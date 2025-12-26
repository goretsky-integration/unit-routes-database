from collections.abc import Iterable

from reports.services.parsers.canceled_orders import (
    DetailedOrder,
    SalesChannel,
)


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
