from matplotlib import gridspec
from pprint import pprint
import datetime as dt
import random
from sqlalchemy import create_engine
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from sys import argv
import mplfinance as mpf

database_path = argv[1] if len(argv) > 1 else "LiveData.db"
lookback_minutes = int(argv[2]) if len(argv) > 2 else 20
engine = create_engine(f"sqlite:///{database_path}")
# symbols = pd.read_sql(
#     'select name from sqlite_master where type="table"', engine
# ).name.to_list()
symbols = [
    arg
    for arg in argv[3:]
    if arg.isalpha() and arg.isupper() and not arg.startswith("/")
]
symbols = symbols if len(symbols) > 0 else ["SOLUSDT"]

if len((period := set(a for a in argv if "period=" in a))) == 1:
    period: set[str]
    ohlc_period = period.pop().split("=")[1]
else:
    ohlc_period = None


# plt.style.use("fivethirtyeight")

import matplotlib.dates as mdates

myFmt = mdates.DateFormatter("%H:%M:%S")
x_vals = []
y_vals = []

index = count()


def qry(symbol: str, lookback_minutes: int) -> pd.DataFrame:
    now = dt.datetime.utcnow()
    before = now - dt.timedelta(minutes=lookback_minutes)
    query = f"""SELECT * FROM '{symbol}' WHERE time >= '{before}' """
    df = pd.read_sql(query, engine)
    return df


def plot_symbols(symbols, lookback_minutes):
    plt.cla()
    dfs = pd.DataFrame()
    for symbol in symbols:
        data: pd.DataFrame = qry(symbol, lookback_minutes=lookback_minutes)
        data.index = pd.to_datetime(data["time"]) + pd.to_timedelta("2h")
        plt.plot(data.index, data["price"], label=symbol)
        # plt.plot(data.index, data['price'].ewm(span=60).mean(), label=f"{symbol} sma60", alpha=0.5)
        dfs[symbol] = data["price"].resample("250ms").mean().ffill()
    mean = dfs.mean(axis="columns")
    plt.plot(mean.index, mean, label="Mean")

    plt.legend(loc="upper left")
    plt.tight_layout()

    plt.xticks(rotation=30)
    plt.gca().xaxis.set_major_formatter(myFmt)


def plot_ohlc(symbol, lookback_minutes):
    data: pd.DataFrame = qry(symbol, lookback_minutes=lookback_minutes)
    data.index = pd.to_datetime(data["time"]) + pd.to_timedelta("2h")

    data["Price"] = data.price
    ohlc = close_to_ohlc(data, period=ohlc_period or "5s")

    price_ax.clear()
    volume_ax.clear()
    price_ax.xaxis.set_major_formatter(myFmt)

    mpf.plot(
        ohlc,
        type="candle",
        style="yahoo",
        mav=[12, 26],
        ax=price_ax,
        volume=volume_ax,
    )


def animate(i):
    # data: pd.DataFrame = pd.read_sql("data.csv")
    if len(symbols) > 1:
        plot_symbols(symbols, lookback_minutes)
    else:
        plot_ohlc(symbols[0], lookback_minutes)


def close_to_ohlc(df, period):
    ohlc = df.Price.resample(rule=period).agg(
        {"Open": "first", "Close": "last", "Low": "min", "High": "max", "Volume": "sum"}
    )
    if "Volume" in df.columns:
        ohlc["Volume"] = df.Volume.resample(period).agg("sum")
    return ohlc


print(f"ci stanno {len(symbols)} simboli.")
pprint(symbols)

fig = plt.gcf()

if len(symbols) == 1:
    spec = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=[3, 1])
    price_ax = fig.add_subplot(spec[0])
    volume_ax = fig.add_subplot(spec[1])


ani = FuncAnimation(fig, animate, interval=500)

plt.tight_layout()
plt.show()
