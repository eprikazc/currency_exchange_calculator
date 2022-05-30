from tortoise.models import Model
from tortoise import fields


class ExchangePair(Model):
    currency1 = fields.CharField(max_length=3)
    currency2 = fields.CharField(max_length=3)

    class Meta:
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
