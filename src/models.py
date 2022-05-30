from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class ExchangePair(Model):
    currency1 = fields.CharField(max_length=3)
    currency2 = fields.CharField(max_length=3)

    class Meta:
        # TODO: add more sophisticated unique constraint
        # to not allow "symmetrical" pairs (such as "USD<>EUR" and "EUR<>USD")
        unique_together = [("currency1", "currency2")]

    def __str__(self):
        return "%s <> %s" % (self.currency1, self.currency2)


class ExchangePairPrice(Model):
    date = fields.DateField()
    exchange_pair = fields.ForeignKeyField("models.ExchangePair")
    price = fields.DecimalField(max_digits=8, decimal_places=4)

    class Meta:
        unique_together = [("exchange_pair", "date")]

    def __str__(self):
        return "%s: %s" % (self.exchange_pair, self.date)


ExchangePair_Pydantic = pydantic_model_creator(ExchangePair, name="ExchangePair")
ExchangePairIn_Pydantic = pydantic_model_creator(
    ExchangePair, name="ExchangePairIn", include=["currency1", "currency2"]
)
