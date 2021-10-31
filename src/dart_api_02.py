import pandas as pd
import pandas_datareader as web
import matplotlib.pyplot as plt
import seaborn as sns
import OpenDartReader
import dart_fss as dart

# import dart_fss_classifier
import pickle
import os

from datetime import datetime
from dotenv import load_dotenv
from icecream import ic

# assert dart_fss_classifier.attached_plugin() == True

if __name__ == "__main__":
    load_dotenv(verbose=True)
    api_key = os.getenv("dart_key")
    dart.set_api_key(api_key=api_key)

    src_data = "data/dart_corp.pkl"
    start = datetime(2020, 1, 1)
    end = datetime(2021, 8, 31)

    # try:
    #     with open(src_data, "rb") as file:
    #         data = pickle.load(file)
    #     print("data reading from file...")
    # except FileNotFoundError:
    #     data = dart.get_corp_list()
    #     with open(src_data, "wb") as file:
    #         pickle.dump(data, file)

    data = dart.get_corp_list()
    info = [corp.info for corp in data.corps]
    df = pd.DataFrame(info)
    df = df.dropna(axis=0, how="any", subset=["stock_code"]).reset_index()
    print(df.tail())

    samsung = data.find_by_corp_name("삼성전자", exactly=True)[0]
    fs = samsung.extract_fs(bgn_de="20100101")
    print(fs)
