import numpy as np
import pandas as pd
import quantstats as qs

from datetime import datetime


if __name__ == "__main__":
    qs.extend_pandas()

    stock = qs.utils.download_returns("FB")
    print(stock)
    stock.plot_earnings(savefig="quantstats/results/fb_earnings.png", start_balance=10000)
    qs.stats.sharpe(stock)
    print(dir(stock))
    print(stock.sharpe())
    print(stock.monthly_returns())
    print(stock.max_drawdown())

    qs.reports.plots(stock, mode="basic")
    qs.reports.metrics(stock, mode="basic")
    qs.reports.html(stock, "AAPL", output="quantstats/results/quantstats-aapl.html")

    stat_func = [f for f in dir(qs.stats) if f[0] != "_"]
    plot_func = [f for f in dir(qs.plots) if f[0] != "_"]
    print(stat_func)
    print(plot_func)
