import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as scs
import statsmodels.api as sm
import statsmodels.tsa.api as smt

from datetime import datetime
from icecream import ic

plt.style.use("seaborn")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["font.size"] = 18
plt.rcParams["axes.titlesize"] = 24
plt.rcParams["axes.labelsize"] = 18
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["legend.fontsize"] = 18
plt.rcParams["figure.titlesize"] = 24
plt.rcParams["figure.dpi"] = 300
plt.rcParams["figure.figsize"] = [12, 8]

if __name__ == "__main__":
    data = pd.read_pickle("./data/stock1.pkl")
    df = data.loc["현대차"]
    df.set_index("date", inplace=True)
    df.info()
    print(df.head())
    # data = data.loc[:, ["date", "close"]].reset_index()
    # prices = data.pivot(index="date", columns="ticker", values="close")
    # prices = prices["2018":"2021"]
    # ic(prices.head(10))