from datetime import date
from decimal import Decimal

from src.crud_utils import create_currency, create_price
from src.models_sqla import ExchangePairPrice


def test_create_price(client, db):
    create_currency(db, code="USD")
    create_currency(db, code="EUR")
    resp = client.post(
        "/prices/",
        json={
            "date": "2020-02-02",
            "sell": "EUR",
            "buy": "USD",
            "value": "1.234",
        },
    )
    assert resp.status_code == 201
    price_obj = db.query(ExchangePairPrice).first()
    assert price_obj.date == date(2020, 2, 2)
    assert price_obj.sell_currency.code == "EUR"
    assert price_obj.buy_currency.code == "USD"
    assert price_obj.price == Decimal("1.2340")


def test_update_price(client, db):
    usd = create_currency(db, code="USD")
    eur = create_currency(db, code="EUR")
    price_obj = create_price(
        db,
        date="2020-02-02",
        sell_currency=eur,
        buy_currency=usd,
        price=Decimal("1.234"),
    )
    resp = client.put(
        "/prices/EUR/USD/2020-02-02",
        json={
            "value": "1.111",
        },
    )
    assert resp.status_code == 200
    price_obj = db.query(ExchangePairPrice).get(price_obj.id)
    assert price_obj.price == Decimal("1.1110")


def test_delete_price(client, db):
    usd = create_currency(db, code="USD")
    eur = create_currency(db, code="EUR")
    create_price(
        db,
        date="2020-02-02",
        sell_currency=eur,
        buy_currency=usd,
        price=Decimal("1.234"),
    )
    resp = client.delete("/prices/EUR/USD/2020-02-02")
    assert resp.status_code == 204
    assert db.query(ExchangePairPrice).all() == []


def test_historical_prices(client, db):
    usd = create_currency(db, code="USD")
    eur = create_currency(db, code="EUR")
    create_price(
        db,
        date="2020-02-02",
        sell_currency=eur,
        buy_currency=usd,
        price=Decimal("1.234"),
    )
    create_price(
        db,
        date="2020-02-03",
        sell_currency=eur,
        buy_currency=usd,
        price=Decimal("1.255"),
    )
    resp = client.get("/prices/EUR/USD?start_date=2020-02-01&end_date=2020-02-03")
    assert resp.status_code == 200
    assert resp.json() == [
        {"date": "2020-02-02", "price": 1.234},
        {"date": "2020-02-03", "price": 1.255},
    ]


def test_get_rate(client, db):
    usd = create_currency(db, code="USD")
    eur = create_currency(db, code="EUR")
    cad = create_currency(db, code="CAD")
    create_price(
        db,
        date="2020-02-02",
        sell_currency=eur,
        buy_currency=usd,
        price=Decimal("1.234"),
    )
    create_price(
        db,
        date="2020-02-02",
        sell_currency=cad,
        buy_currency=usd,
        price=Decimal("0.84"),
    )
    resp = client.get("/prices/EUR/CAD/2020-02-02")
    assert resp.status_code == 200
    assert resp.json() == {"price": 1.468}
