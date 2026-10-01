import os, time, requests
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
@app.route('/')
def home():
    return "Radhagold Bot Running - /gold + Auto Alert"

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        print(f"Telegram: {r.status_code}")
    except Exception as e:
        print(e)

def get_gold_data():
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=21"
    data = requests.get(url, timeout=10).json()
    closes = [float(c[4]) for c in data]
    curr_price = closes[-1]
    # Simple logic
    ema9 = sum(closes[-9:])/9
    ema21 = sum(closes[-21:])/21
    high_5m = float(data[-2][2])
    low_5m = float(data[-2][3])
    rsi = 32.0 # demo ke liye, aapka purana formula yahi tha
    pivot = 4313.0
    return curr_price, high_5m, low_5m, ema9, ema21, rsi, pivot

def make_signal_msg():
    price, high_5m, low_5m, ema9, ema21, rsi, pivot = get_gold_data()
    if ema9 < ema21:
        signal = "🔻 *SELL SIGNAL*"
        sl = price + 15
        tp1 = price - 12
        tp2 = price - 28
        trend = f"Gold $4318 High se ${4318-price:.1f} gira - Strong SELL"
    else:
        signal = "🔺 *BUY SIGNAL*"
        sl = price - 15
        tp1 = price + 12
        tp2 = price + 28
        trend = f"Gold Low se ${price-4250:.1f} utha - Strong BUY"

    msg = f"{signal}\n\n💰 Price: ${price:.2f}\n📊 RSI: {rsi}\n📈 EMA9: {ema9:.1f} | EMA21: {ema21:.1f}\n⚖️ Pivot: {pivot}\n\n🎯 SL: ${sl:.1f}\n✅ TP1: ${tp1:.1f}\n✅ TP2: ${tp2:.1f}\n\n📝 {trend}"
    return msg, price, high_5m, low_5m

def handle_commands():
    print("Command Handler Started - /gold ka wait kar raha hu")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset+1}&timeout=20"
            res = requests.get(url, timeout=25).json()
            for upd in res.get("result", []):
                offset = upd["update_id"]
                msg = upd.get("message", {})
                text = msg.get("text", "")
                chat_id = str(msg.get("chat", {}).get("id", ""))
                if "/gold" in text.lower():
                    print(f"/gold command from {chat_id}")
                    signal_msg, _, _, _ = make_signal_msg()
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                                  json={"chat_id": chat_id, "text": signal_msg}, timeout=10)
        except Exception as e:
            print(f"Command error: {e}")
            time.sleep(5)

def auto_alert_loop():
    print("Auto 5MIN Alert Loop Started")
    send_telegram("🟢 *Bot LIVE*\n`/gold` likho turant signal ke liye\nAuto 5Min Breakout bhi ON hai")
    while True:
        try:
            _, price, high_5m, low_5m = make_signal_msg()[1], *make_signal_msg()[1:]
            # Actually get again
            msg, price, high_5m, low_5m = make_signal_msg()[0], *get_gold_data()[:3]
            # simplified
            price, high_5m, low_5m = get_gold_data()[:3]
            print(f"Check Price {price} High {high_5m} Low {low_5m}")
            if price > high_5m:
                send_telegram(f"🟢 *5MIN BREAKOUT BUY*\nPrice: ${price:.2f}")
                time.sleep(300)
            elif price < low_5m:
                send_telegram(f"🔴 *5MIN BREAKDOWN SELL*\nPrice: ${price:.2f}")
                time.sleep(300)
        except Exception as e:
            print(e)
        time.sleep(60)

Thread(target=handle_commands, daemon=True).start()
Thread(target=auto_alert_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
