from pykrx import stock
from datetime import datetime


if __name__ == "__main__":
    # tickers = stock.get_market_ticker_list()
    # print(tickers)
    stock_code = stock.get_market_ticker_list(market="KOSPI")
    print(len(stock_code))
    stock_code = stock.get_market_ticker_list(market="KOSDAQ")
    print(len(stock_code))
    stock_code = stock.get_market_ticker_list(market="KONEX")
    print(len(stock_code))

    ticker = "005930"
    start = datetime(2016, 10, 1)
    end = datetime(2021, 12, 31)

    df = stock.get_market_fundamental_by_date(fromdate=start, todate=end, ticker=ticker, freq="y")
    print(df.head())
