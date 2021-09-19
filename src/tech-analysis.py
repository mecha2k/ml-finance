import pandas as pd
import matplotlib.pyplot as plt
import backtrader as bt

from icecream import ic

plt.style.use("default")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "Malgun Gothic"
# plt.rcParams["font.size"] = 18
# plt.rcParams["axes.titlesize"] = 24
# plt.rcParams["axes.labelsize"] = 18
# plt.rcParams["xtick.labelsize"] = 14
# plt.rcParams["ytick.labelsize"] = 14
# plt.rcParams["legend.fontsize"] = 18
# plt.rcParams["figure.titlesize"] = 24
plt.rcParams["figure.dpi"] = 150
plt.rcParams["figure.figsize"] = [8, 6]


class SmaStrategy(bt.Strategy):
    params = (("ma_period", 20),)

    def __init__(self):
        # keep track of close price in the series
        self.data_close = self.datas[0].close
        # keep track of pending orders/buy price/buy commission
        self.order = None
        self.price = None
        self.comm = None
        # add a simple moving average indicator
        self.sma = bt.ind.SMA(self.datas[0], period=self.params.ma_period)

    def log(self, txt):
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f"{dt}, {txt}")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # order already submitted/accepted - no action required
            return
        # report executed order
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"BUY EXECUTED --- Price: {order.executed.price:.2f}, "
                    f"Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}"
                )
                self.price = order.executed.price
                self.comm = order.executed.comm
            else:
                self.log(
                    f"SELL EXECUTED --- Price: {order.executed.price:.2f}, "
                    f"Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}"
                )
        # report failed order
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Failed")
        # set no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f"OPERATION RESULT --- Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}")

    def next(self):
        # do nothing if an order is pending
        if self.order:
            return
        # check if there is already a position
        if not self.position:
            # buy condition
            if self.data_close[0] > self.sma[0]:
                self.log(f"BUY CREATED --- Price: {self.data_close[0]:.2f}")
                self.order = self.buy()
        else:
            # sell condition
            if self.data_close[0] < self.sma[0]:
                self.log(f"SELL CREATED --- Price: {self.data_close[0]:.2f}")
                self.order = self.sell()


class BBandStrategy(bt.Strategy):
    params = (
        ("period", 20),
        ("devfactor", 2.0),
    )

    def __init__(self):
        # keep track of close price in the series
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        # keep track of pending orders/buy price/buy commission
        self.order = None
        self.price = None
        self.comm = None
        # add Bollinger Bands indicator and track the buy/sell signals
        self.b_band = bt.ind.BollingerBands(
            self.datas[0], period=self.p.period, devfactor=self.p.devfactor
        )
        self.buy_signal = bt.ind.CrossOver(self.datas[0], self.b_band.lines.bot)
        self.sell_signal = bt.ind.CrossOver(self.datas[0], self.b_band.lines.top)

    def log(self, txt):
        """Logging function"""
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f"{dt}, {txt}")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # order already submitted/accepted - no action required
            return
        # report executed order
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"BUY EXECUTED --- Price: {order.executed.price:.2f}, "
                    f"Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}"
                )
                self.price = order.executed.price
                self.comm = order.executed.comm
            else:
                self.log(
                    f"SELL EXECUTED --- Price: {order.executed.price:.2f}, "
                    f"Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}"
                )
        # report failed order
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Failed")
        # set no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f"OPERATION RESULT --- Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}")

    def next_open(self):
        if not self.position:
            if self.buy_signal > 0:
                # calculate the max number of shares ('all-in')
                size = int(self.broker.getcash() / self.datas[0].open)
                # buy order
                self.log(
                    f"BUY CREATED --- Size: {size}, Cash: {self.broker.getcash():.2f}, "
                    f"Open: {self.data_open[0]}, Close: {self.data_close[0]}"
                )
                self.buy(size=size)
        else:
            if self.sell_signal < 0:
                # sell order
                self.log(f"SELL CREATED --- Size: {self.position.size}")
                self.sell(size=self.position.size)


class RsiSignalStrategy(bt.SignalStrategy):
    params = dict(rsi_periods=14, rsi_upper=70, rsi_lower=30, rsi_mid=50)

    def __init__(self):
        # add RSI indicator
        rsi = bt.indicators.RSI(
            period=self.p.rsi_periods, upperband=self.p.rsi_upper, lowerband=self.p.rsi_lower
        )
        # add RSI from TA-lib just for reference
        bt.talib.RSI(self.data, plotname="TA_RSI")
        # long condition (with exit)
        rsi_signal_long = bt.ind.CrossUp(rsi, self.p.rsi_lower, plot=False)
        self.signal_add(bt.SIGNAL_LONG, rsi_signal_long)
        self.signal_add(bt.SIGNAL_LONGEXIT, -(rsi > self.p.rsi_mid))
        # short condition (with exit)
        rsi_signal_short = -bt.ind.CrossDown(rsi, self.p.rsi_upper, plot=False)
        self.signal_add(bt.SIGNAL_SHORT, rsi_signal_short)
        self.signal_add(bt.SIGNAL_SHORTEXIT, rsi < self.p.rsi_mid)


if __name__ == "__main__":
    data = pd.read_pickle("./data/stock1.pkl")
    df = data.loc["현대차"]
    df.set_index("date", inplace=True)
    df = df.sort_index()["2018-1-1":"2018-12-31"]
    df.info()

    data = bt.feeds.PandasData(dataname=df)

    # cerebro = bt.Cerebro(stdstats=False)
    # cerebro.adddata(data)
    # cerebro.broker.setcash(1000000.0)
    # cerebro.addstrategy(SmaStrategy)
    # cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addobserver(bt.observers.Value)
    # cerebro.addobserver(bt.observers.Broker)
    # cerebro.addobserver(bt.observers.Trades)

    # print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    # cerebro.run()
    # print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    # cerebro.plot(iplot=False, volume=True, width=8, height=5)

    cerebro = bt.Cerebro(stdstats=False, cheat_on_open=True)
    cerebro.addstrategy(RsiSignalStrategy)
    cerebro.adddata(data)
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="time_return")

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    backtest_result = cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
    print(backtest_result[0].analyzers.returns.get_analysis())
    cerebro.plot(iplot=False, volume=False)

    ic(backtest_result[0].analyzers)
    returns_dict = backtest_result[0].analyzers.time_return.get_analysis()
    returns_df = pd.DataFrame(
        list(returns_dict.items()), columns=["report_date", "return"]
    ).set_index("report_date")
    returns_df.plot(title="Portfolio returns")
    plt.tight_layout()
    plt.savefig("images/ch2_im9.png")

