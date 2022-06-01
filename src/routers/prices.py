from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr
from sqlalchemy.orm import joinedload

from src.best_rate_calculator import calculate_best_rate
from src.common import Error
from src.deps import get_db
from src.models_sqla import Currency, ExchangePairPrice

router = APIRouter()


currency_code = constr(max_length=3)


class PriceIn(BaseModel):
    date: date
    sell: str
    buy: str
    value: Decimal


class PriceUpdate(BaseModel):
    value: Decimal


class DatePrice(BaseModel):
    date: date
    price: Decimal

    class Config:
        orm_mode = True


class BestPrice(BaseModel):
    price: Optional[Decimal]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": Error}},
)
def create_price(price: PriceIn, session=Depends(get_db)):
    sell_currency = _get_currency_by_code(session, price.sell)
    buy_currency = _get_currency_by_code(session, price.buy)
    if (
        session.query(ExchangePairPrice)
        .filter_by(
            sell_currency=sell_currency,
            buy_currency=buy_currency,
            date=price.date,
        )
        .first()
    ):
        raise HTTPException(status_code=400, detail="Price already exists")
    if (
        session.query(ExchangePairPrice)
        .filter_by(
            sell_currency=buy_currency,
            buy_currency=sell_currency,
            date=price.date,
        )
        .first()
    ):
        raise HTTPException(status_code=400, detail="Price already exists")
    price_obj = ExchangePairPrice(
        date=price.date,
        sell_currency=sell_currency,
        buy_currency=buy_currency,
        price=price.value,
    )
    session.add(price_obj)
    session.commit()


@router.put(
    "/{sell_currency_code}/{buy_currency_code}/{date}",
    status_code=status.HTTP_200_OK,
    responses={400: {"model": Error}},
)
def update_price(
    sell_currency_code: currency_code,
    buy_currency_code: currency_code,
    date: date,
    price: PriceUpdate,
    session=Depends(get_db),
):
    sell_currency = _get_currency_by_code(session, sell_currency_code)
    buy_currency = _get_currency_by_code(session, buy_currency_code)
    price_record = _get_price_record(
        session, date=date, sell_currency=sell_currency, buy_currency=buy_currency
    )
    price_record.price = price.value
    session.commit()


@router.delete(
    "/{sell_currency_code}/{buy_currency_code}/{date}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": Error}},
)
def delete_price(
    sell_currency_code: currency_code,
    buy_currency_code: currency_code,
    date: date,
    session=Depends(get_db),
):
    sell_currency = _get_currency_by_code(session, sell_currency_code)
    buy_currency = _get_currency_by_code(session, buy_currency_code)
    price_record = _get_price_record(
        session, date=date, sell_currency=sell_currency, buy_currency=buy_currency
    )
    session.delete(price_record)
    session.commit()


@router.get(
    "/{sell_currency_code}/{buy_currency_code}",
    status_code=status.HTTP_200_OK,
    response_model=list[DatePrice],
    responses={400: {"model": Error}},
)
def get_historical_prices(
    sell_currency_code: currency_code,
    buy_currency_code: currency_code,
    start_date: date = None,
    end_date: date = None,
    session=Depends(get_db),
):
    start_date, end_date = _get_start_end_dates(start_date, end_date)
    if (end_date - start_date).days > 180:
        raise HTTPException(
            status_code=400,
            detail="Interval must be shorter than 180 days",
        )
    sell_currency = _get_currency_by_code(session, sell_currency_code)
    buy_currency = _get_currency_by_code(session, buy_currency_code)
    price_records = (
        session.query(ExchangePairPrice)
        .filter(
            ExchangePairPrice.sell_currency == sell_currency,
            ExchangePairPrice.buy_currency == buy_currency,
            ExchangePairPrice.date >= start_date,
            ExchangePairPrice.date <= end_date,
        )
        .order_by(ExchangePairPrice.date)
    )
    return [DatePrice.from_orm(item) for item in price_records]


@router.get(
    "/{sell_currency_code}/{buy_currency_code}/{date}",
    status_code=status.HTTP_200_OK,
    response_model=BestPrice,
    responses={400: {"model": Error}},
)
def get_rate(
    sell_currency_code: currency_code,
    buy_currency_code: currency_code,
    date: date,
    session=Depends(get_db),
):
    # Validate currency codes
    _get_currency_by_code(session, sell_currency_code)
    _get_currency_by_code(session, buy_currency_code)
    query = (
        session.query(ExchangePairPrice)
        .filter_by(date=date)
        .options(
            joinedload(ExchangePairPrice.buy_currency),
            joinedload(ExchangePairPrice.sell_currency),
        )
    )
    data = [
        (item.sell_currency.code, item.buy_currency.code, item.price) for item in query
    ]
    best_rate = calculate_best_rate(sell_currency_code, buy_currency_code, data, 4)
    return BestPrice(price=best_rate)


def _get_start_end_dates(start=None, end=None):
    if start is None and end is None:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    elif start is not None and end is None:
        start_date = start
        end_date = start + timedelta(days=30)
    elif start is None and end is not None:
        end_date = end
        start_date = end - timedelta(days=30)
    else:
        start_date = start
        end_date = end
    return start_date, end_date


def _get_currency_by_code(db_session, code: str):
    currency = db_session.query(Currency).filter_by(code=code).first()
    if currency is None:
        raise HTTPException(
            status_code=400,
            detail=f"Currency '{code}' does not exist",
        )
    else:
        return currency


def _get_price_record(db_session, date, sell_currency, buy_currency):
    price_record = (
        db_session.query(ExchangePairPrice)
        .filter_by(date=date, sell_currency=sell_currency, buy_currency=buy_currency)
        .first()
    )
    if price_record is None:
        raise HTTPException(
            status_code=400,
            detail="Price record does not exist",
        )
    return price_record
