from datetime import date
from decimal import Decimal
from typing import Optional

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from src.best_rate_calculator import calculate_best_rate

DECIMAL_PLACES = 4


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

    data = list(
        await ExchangePairPrice.filter(date=date).values_list(
            "sell_currency__code", "buy_currency__code", "price"
        )
    )
    return calculate_best_rate(
        sell_currency_code, buy_currency_code, data, DECIMAL_PLACES
    )


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
