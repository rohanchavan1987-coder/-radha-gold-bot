import requests, threading, os, time
import yfinance as yf
import pandas as pd
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_live_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=8).json()
        price = float(r['price'])
        if price > 1000: return price
    except: pass
    try:
        df = yf.download("GC=F", period="1d", interval="1m", progress=False)
        return float(df['Close'].iloc[-1])
    except:
        return 4170.0

def get_history():
    try:
        df = yf.download("GC=F", period="5d", interval="15m", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def calc_rsi_ema(df):
    try:
        close = df['Close']
        delta = close.diff()
        gain = delta.where(delta>0,0).rolling(14).mean()
        loss = -delta.where(delta<0,0).rolling(14).mean()
        rs = gain/loss
        rsi = 100 - (100/(1+rs))
        return float(rsi.iloc[-1]), float(close.ewm(span=9).mean().iloc[-1]), float(close.ewm(span=21).mean().iloc[-1]), float((df['High'].iloc[-1]+df['Low'].iloc[-1]+close.iloc[-1])/3)
    except: return 50.0, 0, 0, 0

def make_signal():
    live = get_live_price()
    df = get_history()
    if df is not None and len(df)>30:
        rsi, ema9, ema21, pivot = calc_rsi_ema(df)
    else:
        rsi, ema9, ema21, pivot = 52.0, live-3, live+3, live+10

    if live < ema9:
        sig, sl, tp1, tp2, note = "🔻 SELL SIGNAL", live+15, live-12, live-28, "Gold High se gira - Strong SELL"
    else:
        sig, sl, tp1, tp2, note = "🟢 BUY SIGNAL", live-15, live+12, live+28, "Gold Low se utha - Strong BUY"

    return f"""{sig}
Live 2 Oct

💰 Price: ${live:.2f}
📊 RSI: {rsi:.1f}
📈 EMA9: {ema9:.1f} | EMA21: {ema21:.1f}
⚖️ Pivot: {pivot:.1f}

🎯 SL: ${sl:.1f}
✅ TP1: ${tp1:.1f}
✅ TP2: ${tp2:.1f}

📝 {note}"""

def poll():
    offset=0
    print(">>> /gold Handler LIVE <<<")
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=20", timeout=25).json()
            for u in r.get('result',[]):
                offset=u['update_id']+1
                txt=u.get('message',{}).get('text','')
                chat=str(u.get('message',{}).get('chat',{}).get('id',''))
                if '/gold' in txt.lower() or '/start' in txt.lower():
                    sig=make_signal()
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id":chat,"text":sig})
        except: time.sleep(5)

threading.Thread(target=poll, daemon=True).start()
app=Flask(__name__)
@app.route('/')
def home(): return "Bot Running Live 4170+"
app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
