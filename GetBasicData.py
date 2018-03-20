import pandas as pd
import matplotlib.pyplot as plt

import pandas_datareader.data as web
import datetime

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]

# 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)

# 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)

# 한글로된 컬럼명을 영어로 바꿔준다.
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
code_df.head()

# 종목 이름을 입력하면 종목에 해당하는 코드를 불러와
# 네이버 금융(http://finance.naver.com)에 넣어줌
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    print("요청 URL = {}".format(url))
    return url

item_name = input("Input item: ")
url = get_url(item_name, code_df)

df = pd.DataFrame()

# 일자 데이터를 담을 df라는 DataFrame 정의
df = pd.DataFrame()

# 1페이지에서 20페이지의 데이터만 가져오기
for page in range(1, 21):
    pg_url = '{url}&page={page}'.format(url=url, page=page)
    df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)

# df.dropna()를 이용해 결측값 있는 행 제거
df = df.dropna()

# 한글로 된 컬럼명을 영어로 바꿔줌
df = df.rename(columns= {'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})

# 데이터의 타입을 int형으로 바꿔줌
df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)

# 컬럼명 'date'의 타입을 date로 바꿔줌
df['date'] = pd.to_datetime(df['date'])

# 일자(date)를 기준으로 오름차순 정렬
df = df.sort_values(by=['date'], ascending=True)

#date 컬럼을 index로 지정
df.set_index(df['date'], inplace=True)

#기존의 date컬럼 삭제
df = df.drop('date',1)

new_df = df[df['volume'] != 0]
ma5 = new_df['close'].rolling(5).mean()
ma20 = new_df['close'].rolling(20).mean()
ma60 = new_df['close'].rolling(60).mean()
ma120 = new_df['close'].rolling(120).mean()

new_df.insert(len(new_df.columns), "MA5", ma5)
new_df.insert(len(new_df.columns), "MA20", ma20)
new_df.insert(len(new_df.columns), "MA60", ma60)
new_df.insert(len(new_df.columns), "MA120", ma120)

# 상위 5개 데이터 확인
print(new_df.tail(20))

plt.plot(new_df.date, new_df['close'], label="Close")

plt.plot(new_df.date, new_df['MA5'], label="MA5")
plt.plot(new_df.date, new_df['MA20'], label="MA20")
plt.plot(new_df.date, new_df['MA60'], label="MA60")
plt.plot(new_df.date, new_df['MA120'], label="MA120")

plt.legend(loc='best')
plt.grid()
plt.show()