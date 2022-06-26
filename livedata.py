from pprint import pprint
from time import sleep
import unicorn_binance_websocket_api

import pandas as pd
from sqlalchemy import create_engine

# from symbols import symbols
symbols = [
    "BTCUSDT",
    "BTCBUSD",
    "BTCUSDC",
    "ETHUSDC",
    "ETHUSDT",
    "ETHBUSD",
    "SOLUSDT",
    "SOLUSDC",
]

from sys import argv


symbols = {s.lower() for s in symbols}

database_path = argv[1] if len(argv) > 1 else "LiveData.db"
engine = create_engine(f"sqlite:///{database_path}")

ubwa = unicorn_binance_websocket_api.BinanceWebSocketApiManager(exchange="binance.com")
ubwa.create_stream(["trade"], symbols, output="UnicornFy")


def process_stream(stream):
    data = stream.pop_stream_data_from_stream_buffer()
    if data and len(data) > 3:
        dataframe = to_dataframe(data)
        SQLImport(dataframe, data["symbol"], engine)
        return data, dataframe
    return data, None


def to_dataframe(data):
    time = data["trade_time"]
    price = data["price"]
    qty = data["quantity"]
    frame = pd.DataFrame(
        {
            "time": [time],
            "price": [price],
            "quantity": [qty],
        }
    )
    frame.time = pd.to_datetime(frame.time, unit="ms")
    frame.price = frame.price.astype(float)
    frame.quantity = frame.quantity.astype(float)
    return frame


def SQLImport(frame, coin, engine):
    return frame.to_sql(
        coin, engine, index=False, if_exists="append", method="multi", chunksize=64
    )


i = 0

from datetime import datetime

now = datetime.now()
ITER_PER_LOG = 5

while True:
    data, dataframe = process_stream(ubwa)
    if dataframe is None:
        sleep(0.1)
        continue
    i = (i + 1) % ITER_PER_LOG
    # print(f"\r{i}         ", end="")
    if i == 0:
        timedelta = datetime.now() - now
        secs_per_iter = timedelta.total_seconds() / ITER_PER_LOG
        print(
            f"\r{timedelta.total_seconds():.2f} Seconds to do {ITER_PER_LOG} iterations.\t\t\t{secs_per_iter*1e3:.1f} ms/iter avg           ",
            end="",
        )
        i = 0
        now = datetime.now()
