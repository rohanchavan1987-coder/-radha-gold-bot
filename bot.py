import os, time, requests
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print(f"DEBUG - BOT_TOKEN exists: {bool(BOT_TOKEN)}")
print(f"DEBUG - CHAT_ID exists: {bool(CHAT_ID)} | Value: {CHAT_ID}")

app = Flask(__name__)
@app.route('/')
def home():
    return f"Gold Bot Running - TOKEN:{bool(BOT_TOKEN)} CHAT:{bool(CHAT_ID)}"

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print(f"ERROR: Token or ChatID missing! Token={bool(BOT_TOKEN)} Chat={CHAT_ID}")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        print(f"Telegram Response: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_gold():
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=2"
    data = requests.get(url, timeout=10).json()
    prev = data[-2]
    curr = data[-1]
    return float(curr[4]), float(prev[2]), float(prev[3])

def run_bot():
    print("✅ Gold Bot Started - ONLY 5 MIN - FIXED VERSION")
    send_telegram("🟢 *Gold Bot LIVE - 5 MIN ONLY* ✅\nBot Restart Ho Gaya Hai")
    while True:
        try:
            price, high_5m, low_5m = get_gold()
            print(f"Price: {price} | 5m High: {high_5m} Low: {low_5m}")
            if price > high_5m:
                send_telegram(f"🟢 *BUY BREAKOUT* Price `{price:.2f}` > High `{high_5m:.2f}`")
                time.sleep(300)
            elif price < low_5m:
                send_telegram(f"🔴 *SELL BREAKDOWN* Price `{price:.2f}` < Low `{low_5m:.2f}`")
                time.sleep(300)
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(10)
        time.sleep(60)

Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
