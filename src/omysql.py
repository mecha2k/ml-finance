import numpy as np
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import os

from datetime import datetime
from dotenv import load_dotenv

plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)


def load_stock_data(code, start, from_file=False, filename="data/stock.pkl"):
    if from_file:
        df = pd.read_pickle(filename)
    else:
        load_dotenv(verbose=True)
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWD"),
            db=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT")),
            charset="utf8",
        )

        sql = f"select * from price where code = {code} and date > '{start}'"
        df = pd.read_sql(sql, conn)
        df["date"] = df["date"].astype("datetime64[ns]")
        df.drop(columns=["code", "diff"], inplace=True)
        df.set_index("date", inplace=True)
        df.to_pickle(filename)
    df.info()
    print(df.tail())
    print(f"stock data loded and saved to {filename}...")

    return df


if __name__ == "__main__":
    start = datetime(2010, 1, 1)
    end = datetime(2021, 9, 30)
    print(start.strftime("%Y-%m-%d"))

    # df = load_stock_data(
    #     "005930", start.strftime("%Y-%m-%d"), from_file=False, filename="data/삼성전자.pkl"
    # )
    # print(df.describe())

    assets = ["현대차", "삼성전자", "네이버", "카카오"]
    data = map(lambda x: pd.read_pickle(f"data/{x}.pkl"), assets)
    data = pd.concat(data, keys=assets, names=["asset", "date"])
    print(data.head())

    close_df = data[["close"]].reset_index()
    print(close_df.head())
    close_df = close_df.pivot("date", "asset", "close")
    close_df = close_df["2019-1":]
    print(close_df.head())

    close_df.plot(figsize=(8, 6))
    plt.tight_layout()
    plt.savefig("images/stocks.png", dpi=300)

    # for asset in assets:
    #     filename = f"data/{asset}.pkl"
    #     data.append(pd.read_pickle(filename))
    # for i in range(len(assets)):
    #     data[i].info()
    #     print(data[i].describe())

    # def get(tickers, start, end):
    # def data(ticker):
    # return pd.io.data.DataReader(ticker, 'yahoo', start, end)
    # datas = map(data, tickers)
    # return pd.concat(datas, keys=tickers, names=['Ticker', 'Date'])
    # Using
    # this
    # function, we
    # can
    # now
    # load
    # the
    # data
    # for all of our stocks:
    #     In[4]:
    # tickers = ['AAPL', 'MSFT', 'GE', 'IBM', 'AA', 'DAL', 'UAL', 'PEP', 'KO']
    # all_data = get(tickers, start, end)
    # all_data[:5]
