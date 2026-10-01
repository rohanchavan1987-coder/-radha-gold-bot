import os, time, requests, yfinance as yf

BOT_TOKEN =os.getnv("8924651615:AAHgJ73W9_ZWvHl9MZOc3PJVy1lhD7os9U8")
CHAT_ID = os.getenv("8924651615")

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        r = requests.post(url, json=payload, timeout=10)
        print(f"Sent: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def get_gold_data():
    df = yf.download("GC=F", period="2d", interval="5m", progress=False, auto_adjust=True)
    price = float(df['Close'].iloc[-1])
    high_4h = float(df['High'].iloc[-49:-1].max())
    low_4h = float(df['Low'].iloc[-49:-1].min())
    return price, high_4h, low_4h

print("✅ Gold Bot Started")
send_telegram("🟢 *Gold Bot LIVE*\nPair: XAUUSD\nTF: 5 Min\nStatus: Started")

while True:
    try:
        price, high, low = get_gold_data()
        print(f"Checking - Price: {price:.2f} | High: {high:.2f} | Low: {low:.2f}")
        if price > high:
            send_telegram(f"🟢 *XAUUSD BUY*\nPrice: `{price:.2f}`\nLogic: 4H High Breakout\nTF: 5Min")
            time.sleep(600)
        elif price < low:
            send_telegram(f"🔴 *XAUUSD SELL*\nPrice: `{price:.2f}`\nLogic: 4H Low Breakdown\nTF: 5Min")
            time.sleep(600)
    except Exception as e:
        print(f"Loop Error: {e}")
    time.sleep(300)
