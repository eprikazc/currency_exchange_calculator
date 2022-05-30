import os
from typing import List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from tortoise.models import Q

from src.models import (
    ExchangePair,
    ExchangePair_Pydantic,
    ExchangePairIn_Pydantic,
    ExchangePairPrice,
)

app = FastAPI()


class Error(BaseModel):
    detail: str


@app.get("/pairs", response_model=List[ExchangePair_Pydantic])
async def get_pairs():
    return await ExchangePair_Pydantic.from_queryset(ExchangePair.all())


@app.post(
    "/pairs",
    response_model=ExchangePair_Pydantic,
    responses={
        400: {"model": Error},
    },
)
async def create_pair(pair: ExchangePairIn_Pydantic):
    # TODO: Validate if pair already exists
    if await ExchangePair.filter(
        Q(currency1=pair.currency1, currency2=pair.currency2)
        | Q(currency1=pair.currency2, currency2=pair.currency1)
    ).exists():
        raise HTTPException(status_code=400, detail="This pair already exists")
    pair_obj = await ExchangePair.create(**pair.dict(exclude_unset=True))
    return await ExchangePair_Pydantic.from_tortoise_orm(pair_obj)


@app.put(
    "/pairs/{pair_id}",
    response_model=ExchangePair_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_pair(pair_id: int, pair: ExchangePairIn_Pydantic):
    await ExchangePair.filter(id=pair_id).update(**pair.dict(exclude_unset=True))
    return await ExchangePair_Pydantic.from_queryset_single(
        ExchangePair.get(id=pair_id)
    )


@app.get(
    "/pairs/{pair_id}",
    response_model=ExchangePair_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_pair(pair_id: int):
    return await ExchangePair_Pydantic.from_queryset_single(
        ExchangePair.get(id=pair_id)
    )


@app.delete(
    "/pairs/{pair_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": Error},
        400: {"model": Error},
    },
)
async def delete_pair(pair_id: int):
    pair = await ExchangePair.get(id=pair_id)
    has_prices = await ExchangePairPrice.filter(exchange_pair=pair).exists()
    if has_prices:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete pair '{pair}' as it has price records",
        )
    await pair.delete()


TORTOISE_ORM = {
    "connections": {"default": os.environ["DB_URL"]},
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


register_tortoise(
    app,
    config=TORTOISE_ORM,
    add_exception_handlers=True,
)
