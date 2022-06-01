from src.models_sqla import Currency


def create_currency(db_session, code) -> Currency:
    currency_obj = Currency(code=code)
    db_session.add(currency_obj)
    db_session.commit()
    return currency_obj
