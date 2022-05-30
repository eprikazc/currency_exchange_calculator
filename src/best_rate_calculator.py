from decimal import Decimal, localcontext
from typing import Optional

import igraph


def calculate_best_rate(
    sell_currency_code: str,
    buy_currency_code: str,
    data: list[str, str, Decimal],
    decimal_places: int,
) -> Optional[Decimal]:
    """Get best available price to exchange currencies on given date"""

    def _get_path_price(path: list[int]) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = decimal_places
            result = Decimal(1)
            current_node = path.pop(0)
            while path:
                next_node = path.pop(0)
                current_node_code = currency_by_index[current_node]
                next_node_code = currency_by_index[next_node]
                price = prices[f"{current_node_code}>{next_node_code}"]
                result *= price
                current_node = next_node
        return result

    nodes = set()
    for sell_curr, buy_curr, price in data:
        nodes.add(sell_curr)
        nodes.add(buy_curr)
    if (sell_currency_code not in nodes) or (buy_currency_code not in nodes):
        return

    currency_by_index = {}
    index_of_currency = {}
    for index, currency_code in enumerate(sorted(nodes)):
        index_of_currency[currency_code] = index
        currency_by_index[index] = currency_code

    prices = {}
    edges = []
    with localcontext() as ctx:
        ctx.prec = decimal_places
        for sell_curr, buy_curr, price in data:
            prices[f"{sell_curr}>{buy_curr}"] = price
            prices[f"{buy_curr}>{sell_curr}"] = 1 / price
            edges.append((index_of_currency[sell_curr], index_of_currency[buy_curr]))

    g = igraph.Graph(len(nodes), edges)
    paths = g.get_shortest_paths(
        index_of_currency[sell_currency_code],
        to=index_of_currency[buy_currency_code],
        output="vpath",
    )
    not_connected = paths == [[]]
    if not_connected:
        return
    return min([_get_path_price(p) for p in paths])
