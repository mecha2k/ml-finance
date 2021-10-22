import pandas as pd
import backtrader as bt
from icecream import ic


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


class MAcrossover(bt.Strategy):
    params = (
        ("pfast", 20),
        ("pslow", 60),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")  # Comment this line when running optimization

    def __init__(self):
        self.dataclose = self.datas[0].close

        # Order variable will contain ongoing order details/status
        self.order = None

        # Instantiate moving averages
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pfast)
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pslow)

        """ Using the built-in crossover indicator
		self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)"""

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED, {order.executed.price:.2f}")
            elif order.issell():
                self.log(f"SELL EXECUTED, {order.executed.price:.2f}")
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        # Reset orders
        self.order = None

    def next(self):
        """ Logic for using the built-in crossover indicator
		
		if self.crossover > 0: # Fast ma crosses above slow ma
			pass # Signal for buy order
		elif self.crossover < 0: # Fast ma crosses below slow ma
			pass # Signal for sell order
		"""

        # Check for open orders
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades

            # If the 20 SMA is above the 50 SMA
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log(f"BUY CREATE {self.dataclose[0]:2f}")
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
            # Otherwise if the 20 SMA is below the 50 SMA
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.log(f"SELL CREATE {self.dataclose[0]:2f}")
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
        else:
            # We are already in the market, look for a signal to CLOSE trades
            if len(self) >= (self.bar_executed + 5):
                self.log(f"CLOSE CREATE {self.dataclose[0]:2f}")
                self.order = self.close()


if __name__ == "__main__":
    cerebro = bt.Cerebro(stdstats=True)

    # cerebro.addstrategy(RsiSignalStrategy)
    cerebro.addstrategy(MAcrossover)

    data = pd.read_pickle("data/현대차.pkl")
    data = data["2021-1":"2021-12"]
    ic(data.head())

    data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data)
    cerebro.broker.setcash(10000000.0)
    cerebro.broker.setcommission(commission=0.002)
    
    cerebro.addsizer(bt.sizers.SizerFix, stake=20) 

    # cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addobserver(bt.observers.Broker)
    # cerebro.addobserver(bt.observers.Trades)

    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="time_return")

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():,}")
    cerebro.plot(iplot=False, volume=False, dpi=300, width=30, height=20)
