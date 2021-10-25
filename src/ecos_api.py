import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)
api_key = os.getenv("ecos_api")

# import xml.etree.ElementTree as ET

# # 호출하려는 OpenAPI URL를 정의합니다.
# url = "http://ecos.bok.or.kr/api/StatisticItemList/sample/xml/kr/1/1/043Y070/"

# # 정의된 OpenAPI URL을 호출합니다.
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

url = f"http://ecos.bok.or.kr/api/KeyStatisticList/{api_key}/json/kr/1/100/"
resp = requests.get(url)
data = resp.json()
rdata = data["KeyStatisticList"]["row"]

df = pd.DataFrame(rdata)
df.set_index("KEYSTAT_NAME", inplace=True)
print(df.head())
