from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


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
    price = fields.DecimalField(max_digits=8, decimal_places=4)

    class Meta:
        unique_together = [("date", "sell_currency", "buy_currency")]

    def __str__(self):
        return "%s: %s/%s" % (self.date, self.sell_currency, self.buy_currency)


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
