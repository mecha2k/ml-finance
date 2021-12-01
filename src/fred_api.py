import pandas as pd
import pandas_datareader as web
import matplotlib.pyplot as plt
import seaborn as sns
import os

from fredapi import Fred
from datetime import datetime
from dotenv import load_dotenv
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator


if __name__ == "__main__":
    load_dotenv(verbose=True)
    fred = Fred(api_key=os.getenv("fred_key"))

    start = datetime(2019, 1, 1)
    end = datetime(2021, 12, 31)

    # data = fred.get_series("SP500", observation_start=start, observation_end=end)
    # data = data.to_frame().reset_index()
    # data.columns = ["date", "sp500"]
    # data.set_index("date", inplace=True)
    # data.index = pd.to_datetime(data.index)
    # print(data.tail())
    # # print(fred.search("potential gdp").T)

    # SP500 = web.DataReader("SP500", "fred", start, end)
    # print(SP500.tail())

    # data = pd.merge(data, SP500, left_index=True, right_index=True, how="outer")
    # print(data.head())
    # print(data.isna().sum())
    # print(data[data.isna().any(axis=1)])
    # data.plot()
    # plt.show()

    # data = web.DataReader("005930", "naver", start, end)
    # data = data.apply(pd.to_numeric)
    # print(data.tail())
    # print(data.dtypes)
    # print(data.isna().sum())
    # data["Close"].plot()
    # plt.show()

    codes = {
        "WM2NS": "M2 (billions $)",
        "DFF": "Fed rates (%)",
        "UNRATE": "Unemployment rate (%)",
        "CPIAUCSL": "CPI urban (1984=100)",
        "PCU441110441110101": "New Vehicle Sales",
        "ICSA": "Initial Claims",
        "CCSA": "Continued Claims (Insured Unemployment)",
        "ASPUS": "Average Sales Price of Houses Sold ($)",
        "MSACSR": "Monthly Supply of Houses",
        "VIXCLS": "CBOE Volatility Index: VIX",
        "T10YIE": "10-Year Breakeven Inflation Rate",
        "SP500": "S&P 500",
    }

    src_data = "eco_indicator/us_data.pkl"
    # try:
    #     data = pd.read_pickle(src_data)
    #     print("data reading from file...")
    # except FileNotFoundError:
    #     data = web.DataReader(list(codes.keys()), "fred", start, end)
    #     data = data.rename(columns=codes)
    #     data.to_pickle(src_data)
    data = web.DataReader(list(codes.keys()), "fred", start, end)
    data = data.rename(columns=codes)
    data.to_pickle(src_data)
    print(data.tail())

    plt.style.use("seaborn-colorblind")
    plt.rcParams["figure.figsize"] = [12, 8]
    plt.rcParams["figure.dpi"] = 300
    plt.set_cmap("cubehelix")
    sns.set_palette("cubehelix")

    for key, value in codes.items():
        _, ax = plt.subplots()
        ax.plot(data[value].dropna(axis=0))
        ax.axvline(x=datetime(2019, 12, 12), color="r", linestyle="--", linewidth=1)
        ax.set(title=value, xlabel="time", ylabel=key)
        ax.xaxis.set_major_locator(MonthLocator())
        date_form = DateFormatter("%y-%m")
        ax.xaxis.set_major_formatter(date_form)
        plt.grid(alpha=0.5, linestyle="--")
        plt.xticks(rotation=45)
        img_name = "eco_indicator/us_" + key + ".png"
        plt.savefig(img_name, bbox_inches="tight")
