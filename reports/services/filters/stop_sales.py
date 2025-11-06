from collections.abc import Iterable

from reports.services.gateways.dodo_is_api import (
    StopSaleBySalesChannel,
    SalesChannel, ChannelStopType,
)


def filter_not_ended_stop_sales(
    stop_sales: Iterable[StopSaleBySalesChannel],
) -> list[StopSaleBySalesChannel]:
    return [
        stop_sale for stop_sale in stop_sales
        if stop_sale.ended_at_local is None
    ]


def filter_by_sales_channels(
    stop_sales: Iterable[StopSaleBySalesChannel],
) -> list[StopSaleBySalesChannel]:
    sales_channels = {
        SalesChannel.DINE_IN,
        SalesChannel.DELIVERY,
    }
    return [
        stop_sale for stop_sale in stop_sales
        if stop_sale.sales_channel in sales_channels
    ]


def filter_complete_stop_sales(
    stop_sales: Iterable[StopSaleBySalesChannel],
) -> list[StopSaleBySalesChannel]:
    return [
        stop_sale for stop_sale in stop_sales
        if stop_sale.channel_stop_type == ChannelStopType.COMPLETE
    ]


def filter_stop_sales_by_sales_channels(
    stop_sales: Iterable[StopSaleBySalesChannel],
) -> list[StopSaleBySalesChannel]:
    stop_sales = filter_not_ended_stop_sales(stop_sales)
    stop_sales = filter_by_sales_channels(stop_sales)
    stop_sales = filter_complete_stop_sales(stop_sales)
    return stop_sales
