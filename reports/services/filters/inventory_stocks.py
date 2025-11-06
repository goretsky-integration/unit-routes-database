from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from reports.services.gateways.dodo_is_api import InventoryStockItem


def filter_running_out_stock_items(
    items: Iterable[InventoryStockItem],
    threshold: int,
) -> list[InventoryStockItem]:
    return [
        item for item in items
        if item.days_until_balance_runs_out <= threshold
    ]


def is_all_zero(*numbers: int | float) -> bool:
    return all(number == 0 for number in numbers)


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
