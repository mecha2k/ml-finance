import pandas as pd
import matplotlib.pyplot as plt

from zipline.api import order_target, record, symbol
from zipline import run_algorithm


def initialize(context):
    context.i = 0
    context.asset = symbol("AAPL")


def handle_data(context, data):
    # Skip first 300 days to get full windows
    context.i += 1
    if context.i < 300:
        return

    # Compute averages
    # data.history() has to be called with the same params
    # from above and returns a pandas dataframe.
    short_mavg = data.history(context.asset, "price", bar_count=100, frequency="1d").mean()
    long_mavg = data.history(context.asset, "price", bar_count=300, frequency="1d").mean()

    # Trading logic
    if short_mavg > long_mavg:
        # order_target orders as many shares as needed to
        # achieve the desired number of shares.
        order_target(context.asset, 100)
    elif short_mavg < long_mavg:
        order_target(context.asset, 0)

    # Save values for later inspection
    record(AAPL=data.current(context.asset, "price"), short_mavg=short_mavg, long_mavg=long_mavg)


def analyze(context, perf):
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel("portfolio value in $")

    ax2 = fig.add_subplot(212)
    perf["AAPL"].plot(ax=ax2)
    perf[["short_mavg", "long_mavg"]].plot(ax=ax2)

    perf_trans = perf.loc[[t != [] for t in perf.transactions]]
    buys = perf_trans.loc[[t[0]["amount"] > 0 for t in perf_trans.transactions]]
    sells = perf_trans.loc[[t[0]["amount"] < 0 for t in perf_trans.transactions]]
    ax2.plot(buys.index, perf.short_mavg.loc[buys.index], "^", markersize=10, color="m")
    ax2.plot(sells.index, perf.short_mavg.loc[sells.index], "v", markersize=10, color="k")
    ax2.set_ylabel("price in $")
    plt.legend(loc=0)
    plt.savefig("images/dma1.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    result = run_algorithm(
        start=pd.Timestamp("2014-1-1", tz="UTC"),
        end=pd.Timestamp("2018-1-1", tz="UTC"),
        initialize=initialize,
        handle_data=handle_data,
        capital_base=10000000,
        bundle="quandl",
        analyze=analyze,
    )
    # result.to_pickle("data/dma1.pkl")
    print(result)
