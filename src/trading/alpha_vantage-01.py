from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.foreignexchange import ForeignExchange
from dotenv import load_dotenv
import requests
import os

load_dotenv(verbose=True)
api_key = os.getenv("ALPHAVANTAGE_API_KEY")


def forex_pandas():
    app = ForeignExchange(output_format="pandas")
    eurusd = app.get_currency_exchange_intraday("EUR", "USD")

    print(eurusd[0])
    print(eurusd[0].loc["2021-04-03"])  # Narrow output to specific date


def tech_indicators(symbol, fast=12, slow=26, period=9):
    app = TechIndicators(output_format="pandas")
    help(app.get_macd)

    data = app.get_macd(symbol, fastperiod=12, slowperiod=26, signalperiod=9)
    print(data)


def retrieve_stock(symbol):
    # Default - JSON format
    # app = TimeSeries()
    # Valid options for output_format are 'pandas', 'csv'.
    app = TimeSeries(output_format="pandas")
    # app = TimeSeries(output_format='csv')
    help(app)

    data = app.get_daily_adjusted(symbol, outputsize="full")
    print(data)


def retrieve_stock_nolib(symbol):
    base_url = "https://www.alphavantage.co/query?"
    params = {"function": "TIME_SERIES_DAILY_ADJUSTED", "symbol": symbol, "apikey": api_key}

    response = requests.get(base_url, params=params)
    print(response.json())


if __name__ == "__main__":
    retrieve_stock("BTCUSD")
    retrieve_stock_nolib("IBM")
    tech_indicators("AAPL")
    forex_pandas()
