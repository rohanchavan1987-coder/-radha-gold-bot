import os, time, requests
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print("Telegram Sent")
    except Exception as e:
        print(e)

def get_gold_data():
    # PAXG is Gold Token - same price as XAUUSD, but works on Render
    try:
        df = yf.download("PAXG-USD", period="2d", interval="5m", progress=False, auto_adjust=True)
        price = float(df['Close'].iloc[-1])
        high_4h = float(df['High'].iloc[-48:].max()) # Last 48 candles = 4 Hour
        low_4h = float(df['Low'].iloc[-48:].min())
        print(f"Price OK: {price} H:{high_4h} L:{low_4h}")
        return price, high_4h, low_4h
    except Exception as e:
        print(f"yfinance failed: {e}")
        # Fallback API
        r = requests.get("https://api.gold-api.com/price/XAUUSD", timeout=10).json()
        price = float(r['price'])
        return price, price+2, price-2

print("✅ Gold Bot Started - PAXG Version")
send_telegram("🟢 *Gold Bot LIVE*\nPair: XAUUSD (PAXG)\nTF: 5 Min\nStatus: Started ✅")

while True:
    try:
        price, high, low = get_gold_data()
        print(f"CHECK Price:{price:.2f} High:{high:.2f} Low:{low:.2f}")
        if price > high:
            send_telegram(f"🟢 *XAUUSD BUY*\nPrice: `{price:.2f}`\nBreakout: 4H High\nTF: 5Min")
            time.sleep(600)
        elif price < low:
            send_telegram(f"🔴 *XAUUSD SELL*\nPrice: `{price:.2f}`\nBreakdown: 4H Low\nTF: 5Min")
            time.sleep(600)
    except Exception as e:
        print(f"Loop Error: {e}")
    time.sleep(300)
