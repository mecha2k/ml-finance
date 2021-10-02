import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as scs
import statsmodels.api as sm
import statsmodels.tsa.api as smt

from talib import RSI
from datetime import datetime
from icecream import ic

plt.style.use("seaborn")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "D2Coding ligature"
plt.rcParams["font.size"] = 18
plt.rcParams["axes.titlesize"] = 24
plt.rcParams["axes.labelsize"] = 18
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["legend.fontsize"] = 18
plt.rcParams["figure.titlesize"] = 24
plt.rcParams["figure.dpi"] = 300
plt.rcParams["figure.figsize"] = [12, 8]

pd.set_option("display.precision", 2)

if __name__ == "__main__":
    src_data = "./data/stock1.pkl"
    tickers = {"현대차": "A005380", "삼성전자": "A005930", "네이버": "A035420", "카카오": "A035720"}
    data = pd.read_pickle(src_data)
    data = data.reset_index()
    data = data.set_index(["ticker", "date"]).drop("level_1", axis=1).sort_index()
    data1 = data.loc[pd.IndexSlice["현대차", "2018":"2021"], :]
    data2 = data.loc["현대차"]["2018":"2021"]

    ic(data1.head())
    ic(data1.index.names)
    ic(data2.head())
    ic(data2.index.names)

    data2["close"].plot()
    plt.title("현대차")
    plt.savefig("images/stocks01.png", bbox_inches="tight")

    data = data1.copy()
    data["close_vol"] = data["close"].mul(data["volume"], axis=0)
    data["close_vol1"] = (
        data.groupby("ticker", group_keys=False, as_index=True)
        .close_vol.rolling(window=20)
        .mean()
        .fillna(0)
        .mul(1e-3)
        .reset_index(level=0, drop=True)
    )
    data["vol_rank"] = data.groupby("date").close_vol.rank(ascending=False)
    data["rsi"] = data.groupby(level="ticker").close.apply(RSI)
    ic(data.tail())

    fig, ax = plt.subplots(nrows=2, ncols=1)
    data.loc["현대차"]["close"].plot(ax=ax[0])
    data.loc["현대차"]["rsi"].plot(ax=ax[1])
    plt.legend()
    plt.savefig("images/stocks02.png", bbox_inches="tight")

    data = data.copy().loc["현대차"]["2020-01":"2020-06"]
    data = data.close.to_frame()
    data.info()

    lags = [1, 5, 10, 20, 40, 60]
    returns = data.close.pct_change()
    percentiles = [0.0001, 0.001, 0.01]
    percentiles += [1 - p for p in percentiles]
    print(returns.describe(percentiles=percentiles))

    q = 0.0001
    for lag in lags:
        data[f"return_{lag}d"] = (
            data.close.pct_change(lag)
            .pipe(lambda x: x.clip(lower=x.quantile(q), upper=x.quantile(1 - q)))
            .add(1)
            .pow(1 / lag)
            .sub(1)
        )
    for t in [1, 2, 3, 4, 5]:
        for lag in [1, 5, 10, 20]:
            data[f"return_{lag}d_lag{t}"] = data[f"return_{lag}d"].shift(t * lag)
    for t in [1, 5, 10, 20]:
        data[f"target_{t}d"] = data[f"return_{t}d"].shift(-t)
    ic(data.head())

    data.to_csv("data/price_lag.csv")
