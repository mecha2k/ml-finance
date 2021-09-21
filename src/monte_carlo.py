import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import quandl
import os
import pandas_datareader.data as web
import QuantLib as ql

from arch import arch_model
from scipy.stats import norm
from pandas_datareader.famafrench import get_available_datasets
from datetime import date, datetime
from dotenv import load_dotenv
from icecream import ic

plt.style.use("seaborn")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["figure.figsize"] = [8, 5]

load_dotenv(verbose=True)
quandl.ApiConfig.api_key = os.getenv("Quandl")


def simulate_gbm(s_0, mu, sigma, n_sims, T, N, random_seed=42, antithetic_var=False):
    """
    Function used for simulating stock returns using Geometric Brownian Motion.
    Parameters
    ------------
    s_0 : float
        Initial stock price
    mu : float
        Drift coefficient
    sigma : float
        Diffusion coefficient
    n_sims : int
        Number of simulations paths
    T : float
        Length of the forecast horizon, same unit as dt
    N : int
        Number of time increments in the forecast horizon
    random_seed : int
        Random seed for reproducibility
    antithetic_var : bool
        Boolean whether to use antithetic variates approach to reduce variance
    Returns
    -----------
    S_t : np.ndarray
        Matrix (size: n_sims x (T+1)) containing the simulation results.
        Rows respresent sample paths, while columns point of time.
    """

    np.random.seed(random_seed)
    dt = T / N
    # Brownian
    if antithetic_var:
        dW_ant = np.random.normal(scale=np.sqrt(dt), size=(int(n_sims / 2), N + 1))
        dW = np.concatenate((dW_ant, -dW_ant), axis=0)
    else:
        dW = np.random.normal(scale=np.sqrt(dt), size=(n_sims, N + 1))
    # simulate the evolution of the process
    S_t = s_0 * np.exp(np.cumsum((mu - 0.5 * sigma ** 2) * dt + sigma * dW, axis=1))
    S_t[:, 0] = s_0
    return S_t


def gaussian_brownian_motion(data):
    df = data["2020-1-1":"2021-8-31"]

    close = df["close"]
    returns = close.pct_change().dropna()
    print(f"Average return: {100 * returns.mean():.2f}%")

    returns.plot(title="Stock returns")
    plt.tight_layout()
    plt.savefig("images/ch6_im1.png")

    train = returns["2020-1-1":"2020-12-31"]
    test = returns["2021-1-1":"2021-08-31"]

    T = len(test)
    N = len(test)
    S_0 = close.loc[train.index[-1]]
    N_SIM = 100
    mu = train.mean()
    sigma = train.std()

    gbm_simulations = simulate_gbm(S_0, mu, sigma, N_SIM, T, N)

    last_train_date = train.index[-1].date()
    first_test_date = test.index[0].date()
    last_test_date = test.index[-1].date()
    plot_title = f"MonteCarlo Simulation " f"({first_test_date}:{last_test_date})"

    selected_indices = close[last_train_date:last_test_date].index
    index = [date.date() for date in selected_indices]
    gbm_simulations_df = pd.DataFrame(np.transpose(gbm_simulations), index=index)

    ax = gbm_simulations_df.plot(alpha=0.2, legend=False)
    (line_1,) = ax.plot(index, gbm_simulations_df.mean(axis=1), color="red")
    (line_2,) = ax.plot(index, close[last_train_date:last_test_date], color="blue")
    ax.set_title(plot_title, fontsize=16)
    ax.legend((line_1, line_2), ("mean", "actual"))
    plt.tight_layout()
    plt.savefig("images/ch6_im2.png")
    plt.close()


def value_at_risk(data):
    np.random.seed(42)
    assets = data.columns.values
    SHARES = [5, 5, 5, 5]
    T = 1
    N_SIMS = 10 ** 5
    ic(assets)

    returns = data.pct_change().dropna()
    plot_title = f'{" vs. ".join(assets)} returns: 2018-01 - 2018-12'
    returns.plot(title=plot_title)
    plt.tight_layout()
    plt.savefig("images/ch6_im3.png")
    print(f"Correlation between returns: {returns.corr().values[0,1]:.2f}")

    cov_mat = returns.cov()
    ic(cov_mat)

    # 6. Perform the Cholesky decomposition of the covariance matrix:
    chol_mat = np.linalg.cholesky(cov_mat)
    ic(chol_mat)
    # 7. Draw correlated random numbers from Standard Normal distribution:
    rv = np.random.normal(size=(N_SIMS, len(assets)))
    correlated_rv = np.transpose(np.matmul(chol_mat, np.transpose(rv)))

    r = np.mean(returns, axis=0).values
    sigma = np.std(returns, axis=0).values
    S_0 = data.values
    S_0 = data.values[-1, :]
    P_0 = np.sum(SHARES * S_0)
    # 9. Calculate the terminal price of the considered stocks:
    S_T = S_0 * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * correlated_rv)
    # 10. Calculate the terminal portfolio value and calculate the portfolio returns:
    P_T = np.sum(SHARES * S_T, axis=1)
    P_diff = P_T - P_0
    # 11. Calculate VaR:
    P_diff_sorted = np.sort(P_diff)
    percentiles = [0.01, 0.1, 1.0]
    var = np.percentile(P_diff_sorted, percentiles)
    for x, y in zip(percentiles, var):
        print(f"1-day VaR with {100-x}% confidence: {-y:.2f}$")
    df = pd.DataFrame(P_diff)
    print(df.describe())

    df.hist(bins=32, figsize=(8, 6))
    plt.title("Distribution of possible 1-day changes in portfolio value 1-day 99% VaR")
    plt.axvline(var[2], 0, 10000, color="r", linewidth=3)
    plt.tight_layout()
    plt.savefig("images/ch6_im4.png")

    var = np.percentile(P_diff_sorted, 5)
    expected_shortfall = P_diff_sorted[P_diff_sorted <= var].mean()
    print(
        f"The 1-day 95% VaR is {-var:.2f}$, and the accompanying Expected Shortfall is {-expected_shortfall:.2f}$."
    )


if __name__ == "__main__":
    df = pd.read_pickle("./data/stock1.pkl")
    data = df.loc["현대차"]
    data.set_index("date", inplace=True)
    data = data.sort_index()["2010-1":"2021-12"]
    data.info()
    ic(data.head())

    gaussian_brownian_motion(data)

    data = df.loc[:, ["date", "close"]].reset_index()
    data = data.pivot(index="date", columns="ticker", values="close")
    data = data["2019-1":"2021-12"]
    ic(data.head())
    value_at_risk(data)
