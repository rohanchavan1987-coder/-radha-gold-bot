import os, time, requests
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
@app.route('/')
def home():
    return "Gold Bot is Running"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print("Telegram sent")
    except Exception as e:
        print(e)

def get_gold():
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=50"
    data = requests.get(url, timeout=10).json()
    closes = [float(c[4]) for c in data]
    highs = [float(c[2]) for c in data]
    lows = [float(c[3]) for c in data]
    price = closes[-1]
    high_4h = max(highs[-49:-1])
    low_4h = min(lows[-49:-1])
    return price, high_4h, low_4h

def run_bot():
    print("✅ Gold Bot Started")
    send_telegram("🟢 *Gold Bot LIVE*\nPair: XAUUSD\nTF: 5 Min\nStatus: Started ✅")
    while True:
        try:
            price, high, low = get_gold()
            print(f"Price: {price} H:{high} L:{low}")
            if price > high:
                send_telegram(f"🟢 *XAUUSD BUY*\nPrice: `{price:.2f}`\nBreakout 4H High")
                time.sleep(600)
            elif price < low:
                send_telegram(f"🔴 *XAUUSD SELL*\nPrice: `{price:.2f}`\nBreakdown 4H Low")
                time.sleep(600)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(300)

Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
