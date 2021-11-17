import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from icecream import ic


plt.style.use("seaborn")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "D2Coding ligature"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["figure.figsize"] = [8, 5]

if __name__ == "__main__":
    df = pd.read_pickle("data/stock1.pkl")
    df = df.loc[:, ["date", "close"]].reset_index()
    df = df.pivot(index="date", columns="ticker", values="close")
    df = df["2021-1":"2021-12"][["카카오"]]
    df["daily_ret"] = df["카카오"].pct_change()
    df.rename(columns={"카카오": "close"}, inplace=True)
    ic(df.iloc[0]["close"])
    ic(df.iloc[-1]["close"])

    period_ret = df.iloc[-1]["close"] / df.iloc[0]["close"] - 1
    df["cum_ret"] = (df["daily_ret"] + 1).cumprod() - 1
    df["log_ret"] = np.log(df["daily_ret"] + 1)
    df["cum_log_ret"] = df.log_ret.cumsum()
    daily_ret_mean = df["daily_ret"].mean()

    ic(daily_ret_mean)
    ic(period_ret)
    ic(df["cum_ret"][-1])

    df.to_csv("data/kakao.csv", encoding="utf-8-sig")
    ic(df.tail())

    # assets = df.columns.values
    # df.plot(title="Stock prices of the considered assets")
    # plt.tight_layout()
    # plt.savefig("images/ch7_im2.png")
