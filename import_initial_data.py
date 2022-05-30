import argparse
import asyncio
import csv

from init_db import init_db
from src.models import ExchangePair, ExchangePairPrice

parser = argparse.ArgumentParser(description="Import exchange rates data.")
parser.add_argument("csv_file_path", help="Path of the csv file to import")


PairIds = dict[str, int]


async def run_import(csv_file_path: str):
    await init_db()
    with open(csv_file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        pair_ids = await _create_pairs(
            [pair.strip() for pair in reader.fieldnames if pair != "Date"]
        )
        for row in reader:
            await _import_pairs(
                row["Date"],
                pair_ids,
                {pair: price for pair, price in row.items() if pair != "Date"},
            )


async def _create_pairs(pairs: list[str]) -> PairIds:
    pair_ids = {}
    for pair_str in pairs:
        currency1, currency2 = pair_str.split("/")
        pair = await ExchangePair.create(currency1=currency1, currency2=currency2)
        pair_ids[pair_str] = pair.id
    return pair_ids


async def _import_pairs(date: str, pair_ids: PairIds, prices: dict[str, str]):
    for exchange_pair, price in prices.items():
        pair_id = pair_ids[exchange_pair]
        await ExchangePairPrice.create(date=date, exchange_pair_id=pair_id, price=price)


if __name__ == "__main__":
    args = parser.parse_args()
    asyncio.run(run_import(args.csv_file_path))
