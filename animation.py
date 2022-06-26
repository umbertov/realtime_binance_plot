from pprint import pprint
import datetime as dt
import random
from sqlalchemy import create_engine
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from sys import argv

database_path = argv[1] if len(argv) > 1 else "LiveData.db"
lookback_minutes = int(argv[2]) if len(argv) > 2 else 20
engine = create_engine(f"sqlite:///{database_path}")
# symbols = pd.read_sql(
#     'select name from sqlite_master where type="table"', engine
# ).name.to_list()
symbols = [
    arg for arg in argv if arg.isalpha() and arg.isupper() and not arg.startswith("/")
]
symbols = symbols if len(symbols) > 0 else ["SOLUSDT"]


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


def animate(i):
    # data: pd.DataFrame = pd.read_sql("data.csv")
    plt.cla()
    for symbol in symbols:
        data: pd.DataFrame = qry(symbol, lookback_minutes=lookback_minutes)
        data.index = pd.to_datetime(data["time"]) + pd.to_timedelta("2h")
        data = (
            data.resample("500ms").agg("mean").interpolate().ffill()
        )  # .resample("1s").agg("mean")
        y1: pd.Series = data["close_price"]
        plt.plot(data.index, y1, label=symbol)
        plt.plot(data.index, y1.ewm(span=60).mean(), label=f"{symbol} sma60", alpha=0.5)

    plt.xticks(rotation=30)
    plt.gca().xaxis.set_major_formatter(myFmt)

    plt.legend(loc="upper left")
    plt.tight_layout()


print(f"ci stanno {len(symbols)} simboli.")
pprint(symbols)

ani = FuncAnimation(plt.gcf(), animate, interval=2000)

plt.tight_layout()
plt.show()
