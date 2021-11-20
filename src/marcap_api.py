from marcap import marcap_data
from datetime import datetime


if __name__ == "__main__":
    ticker = "005930"

    start = datetime(2019, 1, 1)
    end = datetime(2020, 12, 31)

    # df = marcap_data("2020-01-01", "2020-12-31")
    df = marcap_data(start=start, end=end, code=ticker)
    df = df.resample(rule="Y").last()
    df.to_csv("data/marcap.csv", encoding="utf-8-sig")

    close = int(df.loc["2020", "Close"])
    marketcap = int(df.loc["2020", "Marcap"])
    stock_tot = int(marketcap / close)  # 5969782550
    print(close, marketcap, stock_tot)

    df = marcap_data("2021-11-10")
    print(df.info())
    print(df.head())
