import pandas as pd
import requests
import matplotlib.pyplot as plt
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(verbose=True)
api_key = os.getenv("ecos_api")

# import xml.etree.ElementTree as ET

# url = "http://ecos.bok.or.kr/api/StatisticItemList/sample/xml/kr/1/1/043Y070/"
# response = requests.get(url)

# # http 요청이 성공했을때 API의 리턴값을 가져옵니다.
# if response.status_code == 200:
#     try:
#         contents = response.text
#         ecosRoot = ET.fromstring(contents)
#         if ecosRoot[0].text[:4] in ("INFO", "ERRO"):
#             print(ecosRoot[0].text + " : " + ecosRoot[1].text)
#         else:
#             print(contents)
#     except Exception as e:
#         print(str(e))

# url = f"http://ecos.bok.or.kr/api/KeyStatisticList/{api_key}/json/kr/1/100/"
# resp = requests.get(url)
# data = resp.json()
# rdata = data["KeyStatisticList"]["row"]
#
# df = pd.DataFrame(rdata)
# df.set_index("KEYSTAT_NAME", inplace=True)
# print(df.head())

# 서비스 통계 목록
# url = f"https://ecos.bok.or.kr/api/StatisticTableList/{api_key}/json/kr/1/1000/"
# response = requests.get(url)
# data = response.json()
# data = data["StatisticTableList"]["row"]
#
# df = pd.DataFrame(data)
# df.set_index("STAT_NAME", inplace=True)
# print(len(df))
# print(df.head())

# 통계 세부항목 목록
# service = "StatisticItemList"
# url = f"http://ecos.bok.or.kr/api/{service}/{api_key}/json/kr/1/1000/"
# response = requests.get(url)
# data = response.json()
# data = data["StatisticTableList"]["row"]
#
# df = pd.DataFrame(data)
# df.set_index("STAT_NAME", inplace=True)
# print(len(df))
# print(df.head())

# 통계용어사전


# 통계 조회 조건 설정
codes = {
    "cpi": "021Y125",
    "M2": "001Y406",
    "기준금리": "098Y001",
    "가계대출": "008Y002",
    "ppi": "013Y202",
    "환율": "036Y004",
}
service = "StatisticSearch"

start = datetime(2010, 1, 1)
end = datetime(2021, 10, 1)
counts = end.month + end.year * 12 - (start.month + start.year * 12)

code = codes["환율"]
period = "MM"
url = f"https://ecos.bok.or.kr/api/{service}/{api_key}/json/kr/1/{counts}/"
url += f"{code}/{period}/{start.strftime('%Y%m')}/{end.strftime('%Y%m')}"
print(code)
if code == codes["환율"]:
    url += "/0000001"
print(start.strftime("%Y%m"))
print(counts)
print(url)

response = requests.get(url)
data = response.json()
data = data[service]["row"]

df = pd.DataFrame(data)
df.drop_duplicates(subset="TIME", keep="first", inplace=True)
df["TIME"] = pd.to_datetime(df["TIME"], format="%Y%m")
df = df[["TIME", "DATA_VALUE"]]
df["cpi"] = pd.to_numeric(df["DATA_VALUE"])
df = df.set_index("TIME").sort_index(ascending=True)
df.to_csv("data/cpi.csv")
print(df.dtypes)
print(df.tail(10))

df["cpi"].plot()
plt.show()
