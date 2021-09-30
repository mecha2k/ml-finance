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
plt.rcParams["font.family"] = "AppleGothic"
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
    src_data = "./data/stock1.pkl"
    tickers = {"현대차": "A005380", "삼성전자": "A005930", "네이버": "A035420", "카카오": "A035720"}

    data = pd.read_pickle(src_data)
    data = data.loc[:, ["date", "close"]].reset_index()
    prices = data.pivot(index="date", columns="ticker", values="close")
    prices = prices["2018":"2021"]
    ic(prices.head(10))

    prices.plot()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("images/stocks.png", pad_inches=0.2)

    df = prices[["현대차"]]
    df = df.rename(columns={"현대차": "close"})

    plt.clf()
    df.plot()
    plt.grid(True)
    plt.savefig("images/hmc-01-01.png", pad_inches=0.2)

    df["simple_rtn"] = df.close.pct_change()
    df["log_rtn"] = np.log(df.close / df.close.shift(1))
    df.dropna(axis=0, inplace=True)
    ic(df.head())

    fig, ax = plt.subplots(3, 1, sharex=True)
    df.close.plot(ax=ax[0])
    ax[0].set(title="HMC time series", ylabel="Stock price")
    df.simple_rtn.plot(ax=ax[1])
    ax[1].set(ylabel="Simple returns (%)")
    df.log_rtn.plot(ax=ax[2])
    ax[2].set(xlabel="Date", ylabel="Log returns (%)")
    ax[2].tick_params(axis="x", which="major", labelsize=12)
    plt.tight_layout()
    plt.savefig("images/hmc-01-02.png")

    df_rolling = df[["simple_rtn"]].rolling(window=21).agg(["mean", "std"])
    df_rolling.columns = df_rolling.columns.droplevel(0)
    df_outliers = df.join(df_rolling)

    def indentify_outliers(row, n_sigmas=3):
        x = row["simple_rtn"]
        mu = row["mean"]
        sigma = row["std"]
        if (x > mu + n_sigmas * sigma) | (x < mu - n_sigmas * sigma):
            return 1
        else:
            return 0

    df_outliers["outlier"] = df_outliers.apply(indentify_outliers, axis=1)
    outliers = df_outliers.loc[df_outliers["outlier"] == 1, ["simple_rtn"]]
    ic(outliers)

    fig, ax = plt.subplots()
    ax.plot(df_outliers.index, df_outliers.simple_rtn * 100, color="blue", label="Normal")
    ax.scatter(outliers.index, outliers.simple_rtn * 100, color="red", label="Anomaly")
    ax.set_title("HMC's stock returns")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig("images/hmc-01-03.png")
    plt.close()

    #### Fact 1 - Non-Gaussian distribution of returns
    r_range = np.linspace(min(df.log_rtn), max(df.log_rtn), num=1000)
    mu = df.log_rtn.mean()
    sigma = df.log_rtn.std()
    norm_pdf = scs.norm.pdf(r_range, loc=mu, scale=sigma)

    fig, ax = plt.subplots(1, 2, figsize=(16, 8))
    sns.histplot(df.log_rtn, kde=False, ax=ax[0])
    ax[0].set_title("Distribution of HMC's stock returns")
    ax[0].plot(r_range, norm_pdf, "g", lw=2, label=f"N({mu:.2f}, {sigma**2:.4f})")
    ax[0].legend(loc="upper left")

    # Q-Q plot
    qq = sm.qqplot(df.log_rtn.values, line="s", ax=ax[1])
    ax[1].set_title("Q-Q plot")
    plt.tight_layout()
    plt.savefig("images/hmc-01-04.png")
    plt.close()

    jb_test = scs.jarque_bera(df.log_rtn.values)

    print("---------- Descriptive Statistics ----------")
    print("Range of dates:", min(df.index.date), "-", max(df.index.date))
    print("Number of observations:", df.shape[0])
    print(f"Mean: {df.log_rtn.mean():.4f}")
    print(f"Median: {df.log_rtn.median():.4f}")
    print(f"Min: {df.log_rtn.min():.4f}")
    print(f"Max: {df.log_rtn.max():.4f}")
    print(f"Standard Deviation: {df.log_rtn.std():.4f}")
    print(f"Skewness: {df.log_rtn.skew():.4f}")
    print(f"Kurtosis: {df.log_rtn.kurtosis():.4f}")
    print(f"Jarque-Bera statistic: {jb_test[0]:.2f} with p-value: {jb_test[1]:.2f}")

    #### Fact 2 - Volatility Clustering
    plt.gcf()
    df.log_rtn.plot(title="Daily HMC's stock returns", figsize=(10, 6))
    plt.tight_layout()
    plt.savefig("images/hmc-01-05.png")

    #### Fact 3 - Absence of autocorrelation in returns
    N_LAGS = 50
    SIGNIFICANCE_LEVEL = 0.05
    acf = smt.graphics.plot_acf(df.log_rtn, lags=N_LAGS, alpha=SIGNIFICANCE_LEVEL)
    plt.tight_layout()
    plt.savefig("images/hmc-01-06.png")

    #### Fact 4 - Small and decreasing autocorrelation in squared/absolute returns
    fig, ax = plt.subplots(2, 1, figsize=(12, 10))
    smt.graphics.plot_acf(df.log_rtn ** 2, lags=N_LAGS, alpha=SIGNIFICANCE_LEVEL, ax=ax[0])
    ax[0].set(title="Autocorrelation Plots", ylabel="Squared Returns")
    smt.graphics.plot_acf(np.abs(df.log_rtn), lags=N_LAGS, alpha=SIGNIFICANCE_LEVEL, ax=ax[1])
    ax[1].set(ylabel="Absolute Returns", xlabel="Lag")
    plt.tight_layout()
    plt.savefig("images/hmc-01-07.png")
    plt.close()

    #### Fact 5 - Leverage effect
    df["moving_std_252"] = df[["log_rtn"]].rolling(window=252).std()
    df["moving_std_21"] = df[["log_rtn"]].rolling(window=21).std()

    fig, ax = plt.subplots(3, 1, figsize=(18, 15), sharex=True)
    df.close.plot(ax=ax[0])
    ax[0].set(title="S&P 500 time series", ylabel="Price ($)")
    df.log_rtn.plot(ax=ax[1])
    ax[1].set(ylabel="Log returns (%)")
    df.moving_std_252.plot(ax=ax[2], color="r", label="Moving Volatility 252d")
    df.moving_std_21.plot(ax=ax[2], color="g", label="Moving Volatility 21d")
    ax[2].set(ylabel="Moving Volatility", xlabel="Date")
    ax[2].legend()
    plt.tight_layout()
    plt.savefig("images/hmc-01-08.png")
    plt.close()
