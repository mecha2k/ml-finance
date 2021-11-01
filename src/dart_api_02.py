import pandas as pd
import pandas_datareader as web
import matplotlib.pyplot as plt
import seaborn as sns
import OpenDartReader
import dart_fss as dart
import pickle
import os

from datetime import datetime
from dotenv import load_dotenv
from icecream import ic


if __name__ == "__main__":
    load_dotenv(verbose=True)
    api_key = os.getenv("dart_key")
    dart.set_api_key(api_key=api_key)

    src_data = "data/dart_corp.pkl"
    start = datetime(2020, 1, 1)
    end = datetime(2021, 8, 31)

    try:
        data = pd.read_pickle(src_data)
        print("data reading from file...")
    except FileNotFoundError:
        data = dart.get_corp_list()
        info = [corp.info for corp in data.corps]
        data = pd.DataFrame(info)
        data = data.dropna(axis=0, how="any", subset=["stock_code"]).reset_index()
        data.to_pickle(src_data)
    data.info()
    print(data.tail())

    corp_name = data.corp_name == "삼성전자"
    ic(corp_name)
    ic(data.loc[corp_name]["corp_code"].values[0])

    # samsung = data.find_by_corp_name("삼성전자", exactly=True)[0]
    # fs = samsung.extract_fs(bgn_de="20200101")
    # fs.save()
