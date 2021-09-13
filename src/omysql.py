import numpy as np
import pandas as pd
import pymysql
import os

from datetime import datetime
from dotenv import load_dotenv


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

    assets = ["현대차", "삼성전자", "네이버", "카카오"]
    data = []
    for asset in assets:
        filename = f"data/{asset}.pkl"
        data.append(pd.read_pickle(filename))
    for i in range(len(assets)):
        data[i].info()
        print(data[i].describe())
