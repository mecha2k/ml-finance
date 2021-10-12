import datetime
import backtrader as bt
from strategies import MAcrossover

cerebro = bt.Cerebro(stdstats=False, optreturn=False)

data = bt.feeds.YahooFinanceCSVData(
    dataname="backtrader/samples/TSLA.csv",
    fromdate=datetime.datetime(2016, 1, 1),
    todate=datetime.datetime(2017, 12, 31),
)

cerebro.adddata(data)
# cerebro.broker.setcash(1000000.0)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
cerebro.optstrategy(MAcrossover, pfast=range(5, 20), pslow=range(50, 100))
cerebro.addsizer(bt.sizers.SizerFix, stake=3)

if __name__ == "__main__":
    optimized_runs = cerebro.run()
    cerebro.plot()

    final_results_list = []
    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() - 10000, 2)
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            final_results_list.append(
                [
                    strategy.params.pfast,
                    strategy.params.pslow,
                    PnL,
                    sharpe["sharperatio"],
                ]
            )
    sort_by_sharpe = sorted(final_results_list, key=lambda x: x[3], reverse=True)
    for line in sort_by_sharpe[:5]:
        print(line)
