import datetime
import backtrader as bt


class MyStrategy(bt.Strategy):
    def next(self):
        dt1 = self.datas[0].datetime.date(0).isoformat()
        dt2 = self.datas[0].datetime.date(-1).isoformat()
        print(dt1, dt2, self.datas[0].close[0], self.datas[0].close[-1])  # Print close prices


# Instantiate Cerebro engine
cerebro = bt.Cerebro()

# Set data parameters and add to Cerebro
data = bt.feeds.YahooFinanceCSVData(
    dataname="backtrader/samples/TSLA.csv",
    fromdate=datetime.datetime(2016, 1, 1),
    todate=datetime.datetime(2016, 1, 31),
)

cerebro.adddata(data)

# Add strategy to Cerebro
cerebro.addstrategy(MyStrategy)

# Run Cerebro Engine
cerebro.run()