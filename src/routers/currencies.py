from fastapi import APIRouter, HTTPException, status
from tortoise.models import Q

from src.common import Error
from src.models_tortoise import (
    Currency,
    Currency_Pydantic,
    CurrencyIn_Pydantic,
    ExchangePairPrice,
)

router = APIRouter()


@router.get("/", response_model=list[Currency_Pydantic])
async def list_currency():
    return await Currency_Pydantic.from_queryset(Currency.all())


@router.post(
    "/",
    response_model=Currency_Pydantic,
    responses={
        400: {"model": Error},
    },
)
async def create_currency(currency: CurrencyIn_Pydantic):
    if await Currency.filter(code=currency.code).exists():
        raise HTTPException(status_code=400, detail="This currency already exists")
    currency_obj = await Currency.create(**currency.dict(exclude_unset=True))
    return await Currency_Pydantic.from_tortoise_orm(currency_obj)


@router.put(
    "/{currency_id}",
    response_model=Currency_Pydantic,
    responses={404: {"model": Error}},
)
async def update_currency(currency_id: int, currency: CurrencyIn_Pydantic):
    await Currency.filter(id=currency_id).update(**currency.dict(exclude_unset=True))
    return await Currency_Pydantic.from_queryset_single(Currency.get(id=currency_id))


@router.get(
    "/{currency_id}",
    response_model=Currency_Pydantic,
    responses={404: {"model": Error}},
)
async def get_currency(currency_id: int):
    return await Currency_Pydantic.from_queryset_single(Currency.get(id=currency_id))


@router.delete(
    "/{currency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": Error},
        400: {"model": Error},
    },
)
async def delete_currency(currency_id: int):
    currency = await Currency.get(id=currency_id)
    has_prices = await ExchangePairPrice.filter(
        Q(sell_currency=currency) | Q(buy_currency=currency)
    ).exists()
    if has_prices:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete currency '{currency}' as it has price records",
        )
    await currency.delete()
