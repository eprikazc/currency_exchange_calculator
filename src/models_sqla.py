from sqlalchemy import (
    DECIMAL,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.sqla_base import Base


class Currency(Base):
    __tablename__ = "currency"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)

    def __str__(self):
        return self.code


class ExchangePairPrice(Base):
    __tablename__ = "exchangepairprice"
    __table_args__ = (UniqueConstraint("date", "sell_currency_id", "buy_currency_id"),)

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    sell_currency_id = Column(Integer, ForeignKey("currency.id"))
    buy_currency_id = Column(Integer, ForeignKey("currency.id"))
    price = Column(DECIMAL(precision=8, scale=4))

    sell_currency = relationship("Currency", foreign_keys=[sell_currency_id])
    buy_currency = relationship("Currency", foreign_keys=[buy_currency_id])

    def __str__(self):
        return "%s: %s/%s" % (self.date, self.sell_currency, self.buy_currency)
