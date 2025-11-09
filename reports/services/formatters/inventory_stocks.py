from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from reports.services.filters.inventory_stocks import UnitInventoryStocks
from reports.services.gateways.dodo_is_api import (
    InventoryStockMeasurementUnit,
    InventoryStockItem,
)


MEASUREMENT_UNIT_TO_NAME = {
    InventoryStockMeasurementUnit.KILOGRAM: 'кг',
    InventoryStockMeasurementUnit.LITER: 'л',
    InventoryStockMeasurementUnit.METER: 'м',
    InventoryStockMeasurementUnit.QUANTITY: 'шт',
}


@dataclass(frozen=True, slots=True, kw_only=True)
class UnitInventoryStocksBalance:
    unit_id: UUID
    balance_in_money: float


def compute_balance_in_money_sum(
    units_inventory_stocks: Iterable[UnitInventoryStocks],
) -> list[UnitInventoryStocksBalance]:
    result: list[UnitInventoryStocksBalance] = []
    for unit_stocks in units_inventory_stocks:
        balance_in_money = sum(
            [
                max(inventory_stock_item.balance_in_money, 0)
                for inventory_stock_item
                in unit_stocks.items
            ],
        )
        result.append(
            UnitInventoryStocksBalance(
                unit_id=unit_stocks.unit_id,
                balance_in_money=round(balance_in_money, 2),
            ),
        )
    return result


def group_inventory_stocks(
    items: Iterable[InventoryStockItem],
) -> list[UnitInventoryStocks]:
    unit_id_to_items: dict[UUID, list[InventoryStockItem]] = defaultdict(list)
    for item in items:
        unit_id_to_items[item.unit_id].append(item)
    return [
        UnitInventoryStocks(
            unit_id=unit_id,
            items=items,
        )
        for unit_id, items in unit_id_to_items.items()
    ]


def format_running_out_stock_items(
    unit_name: str,
    items: Iterable[InventoryStockItem],
) -> str:
    items = list(items)

    lines: list[str] = [f'<b>{unit_name}</b>']

    if items:
        lines.append('<b>❗️ На сегодня не хватит ❗️</b>')
    else:
        lines.append('<b>На сегодня всего достаточно</b>')

    items.sort(key=lambda item: item.name)

    for item in items:
        measurement_unit_name = MEASUREMENT_UNIT_TO_NAME.get(
            item.measurement_unit,
            item.measurement_unit,
        )
        lines.append(
            f'📍 {item.name}'
            f' - остаток <b><u>{item.quantity} {measurement_unit_name}</u></b>',
        )

    return '\n'.join(lines)
