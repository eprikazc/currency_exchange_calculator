import argparse
import csv

from src.crud_utils import create_currency
from src.models_sqla import ExchangePairPrice
from src.sqla_base import SessionLocal

parser = argparse.ArgumentParser(description="Import exchange rates data.")
parser.add_argument("csv_file_path", help="Path of the csv file to import")


CurrencyIDs = dict[str, int]


def run_import(csv_file_path: str):
    session = SessionLocal()
    with open(csv_file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        currency_ids = _create_currencies(
            session,
            set(_get_currencies_from_headers(reader.fieldnames)),
        )
        for row in reader:
            for date, currency1, currency2, price in _get_prices_from_row(row):
                price_obj = ExchangePairPrice(
                    date=date,
                    sell_currency_id=currency_ids[currency1],
                    buy_currency_id=currency_ids[currency2],
                    price=price,
                )
                session.add(price_obj)
                session.commit()


def _create_currencies(session, currency_codes: set[str]) -> CurrencyIDs:
    currency_ids = {}
    for code in currency_codes:
        currency = create_currency(session, code=code)
        currency_ids[code] = currency.id
    return currency_ids


def _get_currencies_from_headers(headers: list[str]):
    for field in headers:
        if field == "Date":
            continue
        currency1, currency2 = field.split("/")
        yield currency1
        yield currency2


def _get_prices_from_row(row: dict[str, str]):
    date = row["Date"]
    for field, price in row.items():
        if field == "Date":
            continue
        currency1, currency2 = field.split("/")
        yield date, currency1, currency2, price


if __name__ == "__main__":
    args = parser.parse_args()
    run_import(args.csv_file_path)
