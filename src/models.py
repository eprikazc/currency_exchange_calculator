from datetime import date
from decimal import Decimal, getcontext
from typing import Optional

import igraph
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

DECIMAL_PLACES = 4
getcontext().prec = DECIMAL_PLACES


class Currency(Model):
    code = fields.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.code


class ExchangePairPrice(Model):
    date = fields.DateField()
    sell_currency = fields.ForeignKeyField(
        "models.Currency", related_name="sell_price_set"
    )
    buy_currency = fields.ForeignKeyField(
        "models.Currency", related_name="buy_price_set"
    )
    price = fields.DecimalField(max_digits=8, decimal_places=DECIMAL_PLACES)

    class Meta:
        unique_together = [("date", "sell_currency", "buy_currency")]

    def __str__(self):
        return "%s: %s/%s" % (self.date, self.sell_currency, self.buy_currency)


async def get_best_rate(
    sell_currency_code: str, buy_currency_code: str, date: date
) -> Optional[Decimal]:
    """Get best available price to exchange currencies on given date"""

    def _get_path_price(path: list[int]) -> Decimal:
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

    data = list(
        await ExchangePairPrice.filter(date=date).values_list(
            "sell_currency__code", "buy_currency__code", "price"
        )
    )
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


Currency_Pydantic = pydantic_model_creator(
    Currency, name="Currency", include=["id", "code"]
)
CurrencyIn_Pydantic = pydantic_model_creator(
    Currency, name="CurrencyIn", include=["code"]
)

ExchangePairPrice_Pydantic = pydantic_model_creator(
    ExchangePairPrice, name="ExchangePairPrice"
)
ExchangePairPriceIn_Pydantic = pydantic_model_creator(
    ExchangePairPrice,
    name="ExchangePairPriceIn",
)
