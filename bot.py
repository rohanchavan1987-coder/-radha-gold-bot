import os, time, requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print("Sent to Telegram")
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_gold_data():
    # Binance PAXG = Real Gold Price, works on Render
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=50"
    data = requests.get(url, timeout=10).json()

    closes = [float(c[4]) for c in data] # Close price
    highs = [float(c[2]) for c in data] # High price
    lows = [float(c[3]) for c in data] # Low price

    price = closes[-1]
    # Last 48 candles = 4 hours (5min * 48 = 240min)
    high_4h = max(highs[-49:-1])
    low_4h = min(lows[-49:-1])

    print(f"Gold Price: {price} High4H: {high_4h} Low4H: {low_4h}")
    return price, high_4h, low_4h

print("✅ Gold Bot Started - Binance PAXG")
send_telegram("🟢 *Gold Bot LIVE*\nPair: XAUUSD (PAXG)\nTF: 5 Min\nSource: Binance\nStatus: Running ✅")

while True:
    try:
        price, high, low = get_gold_data()

        if price > high:
            send_telegram(f"🟢 *XAUUSD BUY SIGNAL*\nPrice: `{price:.2f}`\nLogic: 4H High Breakout `{high:.2f}`\nTF: 5 Min")
            time.sleep(600)
        elif price < low:
            send_telegram(f"🔴 *XAUUSD SELL SIGNAL*\nPrice: `{price:.2f}`\nLogic: 4H Low Breakdown `{low:.2f}`\nTF: 5 Min")
            time.sleep(600)

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(300) # 5 min check
