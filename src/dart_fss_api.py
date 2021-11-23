import pandas as pd
import pandas_datareader as web
import matplotlib.pyplot as plt
import seaborn as sns
import OpenDartReader
import FinanceDataReader as fdr
import dart_fss as dart
import os

from marcap import marcap_data
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(verbose=True)
api_key = os.getenv("dart_key")
dart.set_api_key(api_key=api_key)

corp_list = dart.get_corp_list()
samsung = corp_list.find_by_corp_name("삼성전자", exactly=True)[0]
fs = samsung.extract_fs(bgn_de="20100101")
fs.save()
