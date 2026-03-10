import FinanceDataReader as fdr
import requests
from bs4 import BeautifulSoup

# 텔레그램 설정 (본인의 정보로 수정)
TELEGRAM_TOKEN = "8706762299:AAHJaDTb1u7QPZIStr8vKuSymOYppAGTfPQ"
CHAT_ID = "7457453659"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def get_stock_analysis():
    stocks = fdr.StockListing('KRX')
    results = []
    
    # 상위 200개 종목만 테스트 (속도 위함)
    for index, row in stocks.head(200).iterrows():
        code = row['Code']
        name = row['Name']
        
        df = fdr.DataReader(code).tail(2)
        if len(df) < 2: continue
        
        prev_close = df.iloc[0]['Close']
        curr_high = df.iloc[1]['High']
        curr_close = df.iloc[1]['Close']
        prev_vol = df.iloc[0]['Volume']
        curr_vol = df.iloc[1]['Volume']
        
        # 조건: 고가/종가 12% 이상 상승 AND 거래량 200% 이상
        cond1 = ((curr_high - prev_close) / prev_close >= 0.12) or ((curr_close - prev_close) / prev_close >= 0.12)
        cond2 = (curr_vol >= prev_vol * 2)
        
        if cond1 and cond2:
            query = f"{name} 급등 이유 특징주"
            url = f"https://search.naver.com/search.naver?where=news&query={query}"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            news_item = soup.select_one(".news_tit")
            
            reason = news_item.text if news_item else "사유 미검색"
            link = news_item['href'] if news_item else ""
            results.append(f"🚀 *{name}*\n- 상승: {((curr_close-prev_close)/prev_close*100):.1f}%\n- 이유: {reason}")

    if results:
        send_telegram("📢 *급등주 분석 보고서*\n\n" + "\n\n".join(results))
    else:
        send_telegram("조건 만족 종목 없음")

if __name__ == "__main__":
    get_stock_analysis()
