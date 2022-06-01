from fastapi import APIRouter, Depends, HTTPException, status

from src.common import Error
from src.crud_utils import create_currency
from src.deps import get_db
from src.models_sqla import Currency, ExchangePairPrice
from src.schemas import Currency_Pydantic, CurrencyIn_Pydantic

from ._helpers import get_object_or_404

router = APIRouter()


@router.get("/", response_model=list[Currency_Pydantic])
def list_currency(session=Depends(get_db)):
    return session.query(Currency).all()


@router.post(
    "/",
    response_model=Currency_Pydantic,
    responses={
        400: {"model": Error},
    },
    status_code=status.HTTP_201_CREATED,
)
def add_currency(currency: CurrencyIn_Pydantic, session=Depends(get_db)):
    if session.query(Currency).filter_by(code=currency.code).first():
        raise HTTPException(status_code=400, detail="This currency already exists")
    return create_currency(session, **currency.dict())


@router.put(
    "/{currency_id}",
    response_model=Currency_Pydantic,
    responses={404: {"model": Error}},
)
def update_currency(
    currency_id: int, currency: CurrencyIn_Pydantic, session=Depends(get_db)
):
    currency_obj = get_object_or_404(session, Currency, currency_id)
    for field, value in currency.dict(exclude_unset=True).items():
        setattr(currency_obj, field, value)
    session.commit()
    return currency_obj


@router.get(
    "/{currency_id}",
    response_model=Currency_Pydantic,
    responses={404: {"model": Error}},
)
def get_currency(currency_id: int, session=Depends(get_db)):
    return get_object_or_404(session, Currency, currency_id)


@router.delete(
    "/{currency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": Error},
        400: {"model": Error},
    },
)
def delete_currency(currency_id: int, session=Depends(get_db)):
    currency = get_object_or_404(session, Currency, currency_id)
    has_prices = (
        session.query(ExchangePairPrice)
        .filter(
            (ExchangePairPrice.sell_currency_id == currency_id)
            | (ExchangePairPrice.buy_currency_id == currency_id)
        )
        .first()
        is not None
    )
    if has_prices:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete currency '{currency}' as it has price records",
        )
    session.delete(currency)
    session.commit()
