from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, constr

from src.common import Error
from src.models import Currency, ExchangePairPrice, get_best_rate

router = APIRouter()


currency_code = constr(max_length=3)


class PriceIn(BaseModel):
    date: date
    sell: currency_code
    buy: currency_code
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
async def create_price(price: PriceIn):
    sell_currency = await _get_currency_by_code(price.sell)
    buy_currency = await _get_currency_by_code(price.buy)
    if await ExchangePairPrice.filter(
        sell_currency=sell_currency,
        buy_currency=buy_currency,
        date=price.date,
    ).exists():
        raise HTTPException(status_code=400, detail="Price already exists")
    if await ExchangePairPrice.filter(
        sell_currency=buy_currency,
        buy_currency=sell_currency,
        date=price.date,
    ).exists():
        raise HTTPException(
            status_code=400, detail="Price for symmetrical currencies already exists"
        )

    await ExchangePairPrice.create(
        date=price.date,
        sell_currency=sell_currency,
        buy_currency=buy_currency,
        price=price.value,
    )


@router.put(
    "/{sell_currency_code}/{buy_currency_code}/{date}",
    status_code=status.HTTP_200_OK,
    responses={400: {"model": Error}},
)
async def update_price(
    sell_currency_code: currency_code,
    buy_currency_code: currency_code,
    date: date,
    price: PriceUpdate,
):
    sell_currency = await _get_currency_by_code(sell_currency_code)
    buy_currency = await _get_currency_by_code(buy_currency_code)
    price_record = await ExchangePairPrice.get(
        date=date, sell_currency=sell_currency, buy_currency=buy_currency
    )
    price_record.price = price.value
    price_record.save()


@router.delete(
    "/{sell_currency_code}/{buy_currency_code}/{date}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": Error}},
)
async def delete_price(
    sell_currency_code: currency_code, buy_currency_code: currency_code, date: date
):
    sell_currency = await _get_currency_by_code(sell_currency_code)
    buy_currency = await _get_currency_by_code(buy_currency_code)
    price_record = await ExchangePairPrice.get(
        date=date, sell_currency=sell_currency, buy_currency=buy_currency
    )
    price_record.delete()


@router.get(
    "/{sell_currency_code}/{buy_currency_code}",
    status_code=status.HTTP_200_OK,
    response_model=list[DatePrice],
    responses={400: {"model": Error}},
)
async def get_historical_prices(
    sell_currency_code: currency_code,
    buy_currency_code: currency_code,
    start_date: date = None,
    end_date: date = None,
):
    start_date, end_date = _get_start_end_dates(start_date, end_date)
    if (end_date - start_date).days > 180:
        raise HTTPException(
            status_code=400,
            detail="Interval must be shorter than 180 days",
        )
    sell_currency = await _get_currency_by_code(sell_currency_code)
    buy_currency = await _get_currency_by_code(buy_currency_code)
    price_records = await ExchangePairPrice.filter(
        sell_currency=sell_currency,
        buy_currency=buy_currency,
        date__gte=start_date,
        date__lte=end_date,
    ).order_by("date")
    return [DatePrice.from_orm(item) for item in price_records]


@router.get(
    "/{sell_currency_code}/{buy_currency_code}/{date}",
    status_code=status.HTTP_200_OK,
    response_model=BestPrice,
    responses={400: {"model": Error}},
)
async def get_rate(
    sell_currency_code: currency_code,
    buy_currency_code: currency_code,
    date: date,
):
    # Validate currencies
    await _get_currency_by_code(sell_currency_code)
    await _get_currency_by_code(buy_currency_code)
    best_rate = await get_best_rate(sell_currency_code, buy_currency_code, date)
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


async def _get_currency_by_code(code: str):
    currency = await Currency.filter(code=code).first()
    if currency is None:
        raise HTTPException(
            status_code=400,
            detail=f"Currency '{code}' does not exist",
        )
    else:
        return currency
