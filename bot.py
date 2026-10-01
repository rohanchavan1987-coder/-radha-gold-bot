import os, time, requests
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
@app.route('/')
def home():
    return "Gold Bot Running - 5 MIN Only"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print("Telegram sent")
    except Exception as e:
        print(e)

def get_gold():
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=2"
    data = requests.get(url, timeout=10).json()
    prev_candle = data[-2] # pichla 5 min candle
    curr_candle = data[-1] # chal raha candle

    prev_high = float(prev_candle[2])
    prev_low = float(prev_candle[3])
    curr_price = float(curr_candle[4])

    return curr_price, prev_high, prev_low

def run_bot():
    print("✅ Gold Bot Started - ONLY 5 MIN")
    send_telegram("🟢 *Gold Bot LIVE*\nPair: XAUUSD\nLogic: *5 Min Candle Breakout*\n4H Filter Removed ✅")
    while True:
        try:
            price, high_5m, low_5m = get_gold()
            print(f"Price: {price} | 5m High: {high_5m} Low: {low_5m}")

            if price > high_5m:
                send_telegram(f"🟢 *XAUUSD BUY - 5MIN BREAKOUT*\nPrice: `{price:.2f}`\nBroke 5Min High: `{high_5m:.2f}`")
                time.sleep(300) # 5 min ruk jao duplicate na aaye
            elif price < low_5m:
                send_telegram(f"🔴 *XAUUSD SELL - 5MIN BREAKDOWN*\nPrice: `{price:.2f}`\nBroke 5Min Low: `{low_5m:.2f}`")
                time.sleep(300)

        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60) # Har 1 min check karega

Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
