import numpy as np
import pandas as pd
import pymysql
import os

from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv(verbose=True)

    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWD"),
        db=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
        charset="utf8",
    )

    sql = "select * from price where code = 005380 and date > '2021-05-01'"
    df = pd.read_sql(sql, conn)
    df["date"] = df["date"].astype("datetime64[ns]")
    df.drop(columns=["code", "diff"], inplace=True)
    df.set_index("date", inplace=True)
    df.info()
    print(df.head())
