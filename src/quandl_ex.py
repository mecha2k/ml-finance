import quandl
import os

from dotenv import load_dotenv
from icecream import ic

load_dotenv(verbose=True)
quandl.ApiConfig.api_key = os.getenv("Quandl")
data = quandl.get("BCHARTS/BITFLYERUSD", start_date="2020-05-07", end_date="2020-05-07")

print(data)
