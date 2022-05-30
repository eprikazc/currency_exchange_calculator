from datetime import date
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, constr

from src.common import Error
from src.models import Currency, ExchangePairPrice

router = APIRouter()


currency_code = constr(max_length=3)


class PriceIn(BaseModel):
    date: date
    sell: currency_code
    buy: currency_code
    value: Decimal


class PriceUpdate(BaseModel):
    value: Decimal


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


async def _get_currency_by_code(code: str):
    currency = await Currency.filter(code=code).first()
    if currency is None:
        raise HTTPException(
            status_code=400,
            detail=f"Currency '{code}' does not exist",
        )
    else:
        return currency
