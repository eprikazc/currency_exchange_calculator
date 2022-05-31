from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from src.models_sqla import Currency, ExchangePairPrice

Currency_Pydantic = sqlalchemy_to_pydantic(Currency)
CurrencyIn_Pydantic = sqlalchemy_to_pydantic(Currency, exclude=["id"])

ExchangePairPrice_Pydantic = sqlalchemy_to_pydantic(
    ExchangePairPrice,
    exclude=["id"],
)
