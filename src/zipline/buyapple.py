import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as web

from zipline.api import order, record, symbol
from zipline import run_algorithm


def initialize(context):
    pass


def handle_data(context, data):
    order(symbol("AAPL"), 10)
    record(AAPL=data.current(symbol("AAPL"), "price"))


if __name__ == "__main__":
    start = pd.Timestamp("2014")
    end = pd.Timestamp("2018")

    sp500 = web.DataReader("SP500", "fred", start, end).SP500
    benchmark_returns = sp500.pct_change()

    data = run_algorithm(
        start=pd.Timestamp("2016-1-1", tz="UTC"),
        end=pd.Timestamp("2018-1-1", tz="UTC"),
        initialize=initialize,
        handle_data=handle_data,
        capital_base=10000000,
        bundle="quandl",
        benchmark_returns=benchmark_returns,
        data_frequency="daily",
    )
    # data.to_pickle("data/buyapple.pkl")
    print(data.head())

    ax1 = plt.subplot(211)
    data.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel("Portfolio Value")
    ax2 = plt.subplot(212, sharex=ax1)
    data.AAPL.plot(ax=ax2)
    ax2.set_ylabel("AAPL Stock Price")
    plt.show()
