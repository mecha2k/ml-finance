import pandas as pd
import matplotlib.pyplot as plt
import os

from fredapi import Fred
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(verbose=True)
api_key = os.getenv("fred_key")

if __name__ == "__main__":
    fred = Fred(api_key=api_key)
    data = fred.get_series("SP500")
    print(data.type)
    # data.reset_index(inplace=True)
    # data.columns = ["date", "sp500"]
    # data.set_index("date", inplace=True)
    print(data.head())
    print(fred.search("potential gdp").T)

    data.plot()
    plt.show()
