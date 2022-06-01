from src.models_sqla import Currency, ExchangePairPrice


def create_currency(db_session, code) -> Currency:
    currency_obj = Currency(code=code)
    db_session.add(currency_obj)
    db_session.commit()
    return currency_obj


def create_price(db_session, date, sell_currency, buy_currency, price) -> Currency:
    price_obj = ExchangePairPrice(
        date=date,
        sell_currency=sell_currency,
        buy_currency=buy_currency,
        price=price,
    )
    db_session.add(price_obj)
    db_session.commit()
    return price_obj
