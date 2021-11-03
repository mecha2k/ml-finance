import pandas as pd
import pandas_datareader as web
import matplotlib.pyplot as plt
import seaborn as sns
import OpenDartReader
import FinanceDataReader as fdr
import os

from datetime import datetime
from dotenv import load_dotenv
from icecream import ic

fs_col_names = {
    "rcept_no": "접수번호",
    "bsns_year": "사업연도",
    "corp_code": "회사코드",
    "stock_code": "종목코드",
    "reprt_code": "보고서코드",
    "account_id": "계정ID",
    "account_nm": "계정명",
    "account_detail": "계정상세",
    "fs_div": "개별/연결구분",
    "fs_nm": "개별/연결명",
    "sj_div": "재무제표구분",
    "sj_nm": "재무제표명",
    "thstrm_nm": "당기명",
    "thstrm_dt": "당기일자",
    "thstrm_amount": "당기금액",
    "thstrm_add_amount": "당기누적금액",
    "frmtrm_nm": "전기명",
    "frmtrm_dt": "전기일자",
    "frmtrm_amount": "전기금액",
    "frmtrm_q_nm": "전기명(분/반기)",
    "frmtrm_q_amount": "전기금액(분/반기)",
    "frmtrm_add_amount": "전기누적금액",
    "bfefrmtrm_nm": "전전기명",
    "bfefrmtrm_dt": "전전기일자",
    "bfefrmtrm_amount": "전전기금액",
    "ord": "계정과목 정렬순서",
}
rep_codes = {"1분기": "11013", "반기": "11012", "3분기": "11014", "연간": "11011"}
idx = pd.MultiIndex


def get_corp_fs(corp_code, start, end):
    corp_fs, corp_fs_all = [], []
    for t in pd.date_range(start=start, end=end, freq="A"):
        rep_times = {
            "1분기": datetime(t.year, 3, 31),
            "반기": datetime(t.year, 6, 30),
            "3분기": datetime(t.year, 9, 30),
            "연간": datetime(t.year, 12, 31),
        }

        fs_brf, fs_all = [], []
        for key, value in rep_codes.items():
            fs = dart.finstate(corp_code, t.year, reprt_code=value)
            fs.rename(columns=fs_col_names, inplace=True)
            fs = fs.loc[(fs["개별/연결구분"] == "CFS")]
            fs = fs[["계정명", "당기금액"]].set_index("계정명")
            fs_brf.append(fs)

            fs = dart.finstate_all(corp_code, t.year, reprt_code=value)
            fs.rename(columns=fs_col_names, inplace=True)
            fs = fs.loc[(fs["재무제표구분"] == "BS") | (fs["재무제표구분"] == "CIS") | (fs["재무제표구분"] == "IS")]
            fs = fs[["계정명", "당기금액"]].set_index("계정명")
            fs_all.append(fs)
        y_fs_brf = pd.concat(fs_brf, keys=rep_times.values(), names=["시간", "계정명"])
        y_fs_all = pd.concat(fs_all, keys=rep_times.values(), names=["시간", "계정명"])
        corp_fs.append(y_fs_brf)
        corp_fs_all.append(y_fs_all)

    return pd.concat(corp_fs), pd.concat(corp_fs_all)


if __name__ == "__main__":
    load_dotenv(verbose=True)
    api_key = os.getenv("dart_key")
    dart = OpenDartReader(api_key)
    dart_corp = dart.corp_codes.copy()

    corp_list = {"삼성전자": "005930", "NAVER": "035420", "카카오": "035720", "현대차": "005380"}

    start = datetime(2016, 1, 1)
    end = datetime(2020, 12, 31)

    # corp_fs, corp_fs_all = [], []
    # for name, code in corp_list.items():
    #     corp_name = dart_corp.loc[dart_corp.stock_code == code, "corp_name"].values[0]
    #     fs, fs_all = get_corp_fs(corp_code=code, start=start, end=end)
    #     corp_fs.append(fs)
    #     corp_fs_all.append(fs_all)
    #     print(f"{corp_name} fs downloaded...")
    # corp_fs = pd.concat(corp_fs, axis=0, keys=corp_list.keys())
    # corp_fs_all = pd.concat(corp_fs_all, axis=0, keys=corp_list.keys())
    # corp_fs.to_pickle("data/corp_fs.pkl")
    # corp_fs_all.to_pickle("data/corp_fs_all.pkl")

    corp_fs = pd.read_pickle("data/corp_fs.pkl")
    corp_fs_all = pd.read_pickle("data/corp_fs_all.pkl")

    ticker = "삼성전자"
    samsung = [corp_fs.loc[ticker], corp_fs_all.loc[ticker]]
    samsung = pd.concat(samsung)

    annual = pd.date_range(start=start, end=end, freq="A")
    samsung = samsung.loc[annual]
    # samsung = samsung.loc[annual].reset_index().pivot(index="계정명", columns="시간", values="당기금액")
    samsung.to_csv("data/fs_samsung.csv", encoding="utf-8-sig")
    print(samsung.head())

    idx = pd.IndexSlice
    print(samsung.loc[idx["2020", "매출액"], :].values[0][0])

    account = ["매출액", "영업이익", "법인세차감전 순이익", "당기순이익", "자산총계", "부채총계", "자본총계", "기본주당이익(손실)"]
    df = samsung.loc[idx["2020", account], :]
    df = df["당기금액"].str.replace(",", "").astype(int)
    print(df)
    print(df.dtypes)

    # print(len(data))
    # data = data["당기금액"].to_numpy()
    # print(data.head(10))
    # data = pd.to_numeric(data)
    # print(data)

    # aa = samsung.loc["2020"]
    # bb = aa.loc["매출액"]
    # print(aa)
    # print(bb)

    # df = fdr.DataReader(corp_list["삼성전자"], start=start, end=end)
    # print(df.tail())

    # samsung = (
    #     samsung.reset_index()
    #     .drop_duplicates(subset="계정명", keep="first")
    #     .set_index(["시간", "계정명"])
    #     .sort_index(level=0)
    # )

    # config = {
    #     "title": "삼성전자",
    #     "width": 600,
    #     "height": 300,
    #     "volume": True,
    # }
    # fdr.chart.config(config=config)
    # fdr.chart.plot(df)
    # plt.show()

    # print(*corp_list.values())
    # aa = dart.xbrl_taxonomy("BS1")
    # aa.to_csv("data/xbrl_tax.csv", encoding="utf-8-sig")

    # fs = dart.finstate("005930, 035720, 005380", "2020", reprt_code="11011")
    # fs.rename(columns=fs_col_names, inplace=True)
    # fs.to_csv("data/corp_fs.csv", encoding="utf-8-sig")

    # corp_data[0].to_csv("data/samsung.csv", encoding="utf-8-sig")
    # corp_data[1].to_csv("data/kakao.csv", encoding="utf-8-sig")

    # dup = corp_data[0].index.duplicated()
    # print(corp_data[0].loc[dup])
    # corp_data[0].to_csv("data/corp_fs.csv", encoding="utf-8-sig")
    # dup = corp_data[1].index.duplicated(keep="first")
    # print(corp_data[1].loc[dup])
    # print(corp_data[1].index.duplicated())
    # corp_fs = pd.concat(corp_data, axis=1, join="inner")
    # corp_fs.to_csv("data/corp_fs.csv", encoding="utf-8-sig")
    #
    # corp_fs = pd.read_csv("data/corp_fs.csv", encoding="utf-8-sig")
    # print(corp_fs.tail(16))
    # print(corp_fs.isna().any(axis=0))
    # print(corp_fs.isna().any(axis=1))
    # idx = corp_fs.index[corp_fs.isna().any(axis=1)]
    # print(corp_fs.loc[idx])

    # res.to_csv("data/samsung2.csv")
    # print(res)

    # fs = dart.finstate_all("035720", "2020", reprt_code="11011")
    # fs.rename(columns=fs_col_names, inplace=True)
    # fs.to_csv("data/kakao1.csv", encoding="utf-8-sig")
    # print(fs)
    # print(fs.info())
    # print(fs.head(20))

    # print(fs.계정명)
    # fs.to_csv("data/samsung.csv")

    # fs_all = dart.finstate_all(name, 2018)
    # fs_all.to_csv("data/samsung1.csv")
    # fs_all.info()

    # print(data.stock_code[data.stock_code == " "].value_counts())
    # data = data.loc[data.stock_code != " "]
    # print(data.loc[data.stock_code == "005930"])
    # data = data.dropna(axis=0, how="any", subset=["stock_code"])
    # print(data.info())
    # print(data.head())
    # data = dart.list("005930", start=start, end=end)
    # print(data)
    # data = dart.list("005930", start="2010-01-01", end="2021-12-31")
    # data.info()
    # ic(data.head())
    # ic(dart.company("005930"))
    # ic(dart.xbrl_taxonomy("BS1"))
    # data = dart.finstate("005930, 000660, 005380", 2018)
    # print(data)

    # samsung = dart.finstate("삼성전자", 2018)
    # print(samsung)

    # # == 1. 공시정보 검색 ==
    # # 삼성전자 2019-07-01 하루 동안 공시 목록 (날짜에 다양한 포맷이 가능합니다)
    # dart.list('005930', end='2019-7-1')

    # # 삼성전자 상장이후 모든 공시 목록 (5,142 건+)
    # dart.list('005930', start='1900')

    # # 삼성전자 2010-01-01 ~ 2019-12-31 모든 공시 목록 (2,676 건)
    # dart.list('005930', start='2010-01-01', end='2019-12-31')

    # # 삼성전자 1999-01-01 이후 모든 정기보고서
    # dart.list('005930', start='1999-01-01', kind='A', final=False)

    # # 삼성전자 1999년~2019년 모든 정기보고서(최종보고서)
    # dart.list('005930', start='1999-01-01', end='2019-12-31', kind='A')

    # # 2020-07-01 하루동안 모든 공시목록
    # dart.list(end='20200701')

    # # 2020-01-01 ~ 2020-01-10 모든 회사의 모든 공시목록 (4,209 건)
    # dart.list(start='2020-01-01', end='2020-01-10')

    # # 2020-01-01 ~ 2020-01-10 모든 회사의 모든 공시목록 (정정된 공시포함) (4,876 건)
    # dart.list(start='2020-01-01', end='2020-01-10', final=False)

    # # 2020-07-01 부터 현재까지 모든 회사의 정기보고서
    # dart.list(start='2020-07-01', kind='A')

    # # 2019-01-01 ~ 2019-03-31 모든 회사의 정기보고서 (961건)
    # dart.list(start='20190101', end='20190331', kind='A')

    # 기업의 개황정보
    # print(dart.company("005930"))

    # # 회사명에 삼성전자가 포함된 회사들에 대한 개황정보
    # print(dart.company_by_name("삼성전자"))

    # # 삼성전자 사업보고서 (2018.12) 원문 텍스트
    # xml_text = dart.document('20190401004781')

    # # ==== 2. 사업보고서 ====
    # # 삼성전자(005930), 배당관련 사항, 2018년
    # dart.report('005930', '배당', 2018)

    # # 서울반도체(046890), 최대주주 관한 사항, 2018년
    # dart.report('046890', '최대주주', 2018)

    # # 서울반도체(046890), 임원 관한 사항, 2018년
    # dart.report('046890', '임원', 2018)

    # # 삼성바이오로직스(207940), 2019년, 소액주주에 관한 사항
    # dart.report('207940', '소액주주', '2019')

    # ==== 3. 상장기업 재무정보 ====
    # 삼성전자 2018 재무제표
    # fs = dart.finstate("삼성전자", 2018)  # 사업보고서
    # print(fs)

    # # 삼성전자 2018Q1 재무제표
    # dart.finstate('삼성전자', 2018, reprt_code='11013')

    # # 여러종목 한번에
    # dart.finstate('00126380,00164779,00164742', 2018)
    # dart.finstate('005930, 000660, 005380', 2018)
    # dart.finstate('삼성전자, SK하이닉스, 현대자동차', 2018)

    # # 단일기업 전체 재무제표 (삼성전자 2018 전체 재무제표)
    # dart.finstate_all('005930', 2018)

    # # 재무제표 XBRL 원본 파일 저장 (삼성전자 2018 사업보고서)
    # dart.finstate_xml('20190401004781', save_as='삼성전자_2018_사업보고서_XBRL.zip')

    # # XBRL 표준계정과목체계(계정과목)
    # dart.xbrl_taxonomy('BS1')

    # # ==== 4. 지분공시 ====
    # # 대량보유 상황보고 (종목코드, 종목명, 고유번호 모두 지정 가능)
    # dart.major_shareholders('삼성전자')

    # # 임원ㆍ주요주주 소유보고 (종목코드, 종목명, 고유번호 모두 지정 가능)
    # dart.major_shareholders_exec('005930')

    # # ==== 5. 확장 기능 ====
    # # 지정한 날짜의 공시목록 전체 (시간 정보 포함)
    # dart.list_date_ex('2020-01-03')

    # # 개별 문서 제목과 URL
    # rcp_no = '20190401004781' # 삼성전자 2018년 사업보고서
    # dart.sub_docs(rcp_no)

    # # 제목이 잘 매치되는 순서로 소트
    # dart.sub_docs('20190401004781', match='사업의 내용')

    # # 첨부 문서 제목과 URL
    # dart.attach_doc_list(rcp_no)

    # # 제목이 잘 매치되는 순서로 소트
    # dart.attach_doc_list(rcp_no, match='감사보고서')

    # # 첨부 파일 제목과 URL
    # dart.attach_file_list(rcp_no)
