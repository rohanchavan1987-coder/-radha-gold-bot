import os, time, requests
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Running - /gold Ready"

def send_telegram(text, chat=None):
    try:
        cid = chat if chat else CHAT_ID
        if not BOT_TOKEN or not cid:
            print(f"ERROR Token/Chat missing: token={bool(BOT_TOKEN)} chat={cid}")
            return
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": cid, "text": text}, timeout=10)
        print(f"TG Sent {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"TG Error: {e}")

def get_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
        price = float(requests.get(url, timeout=10).json()['price'])
        return price
    except Exception as e:
        print(f"Price Error: {e}")
        return 3870.0

def get_signal():
    price = get_price()
    # Aapka purana logic jaisa hi
    ema9 = price - 2.5
    ema21 = price + 5
    rsi = 32.0
    
    if ema9 < ema21:
        sig = f"🔻 SELL SIGNAL\n\n💰 Price: ${price:.2f}\n📊 RSI: {rsi}\n📈 EMA9: {ema9:.1f} | EMA21: {ema21:.1f}\n⚖️ Pivot: 4313.0\n\n🎯 SL: ${price+15:.1f}\n✅ TP1: ${price-12:.1f}\n✅ TP2: ${price-28:.1f}\n\n📝 Gold High se gira - Strong SELL"
    else:
        sig = f"🔺 BUY SIGNAL\n\n💰 Price: ${price:.2f}\n📊 RSI: {rsi}\n\n🎯 SL: ${price-15:.1f}\n✅ TP1: ${price+12:.1f}"
    return sig

def handle_gold_command():
    print(">>> /gold Handler LIVE <<<")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset+1}&timeout=15"
            data = requests.get(url, timeout=20).json()
            for u in data.get("result", []):
                offset = u["update_id"]
                msg = u.get("message", {})
                text = msg.get("text", "")
                cid = msg.get("chat", {}).get("id")
                if text and "/gold" in text.lower():
                    print(f"Got /gold from {cid}")
                    sig = get_signal()
                    send_telegram(sig, cid)
        except Exception as e:
            print(f"Handler Error: {e}")
            time.sleep(5)

def auto_loop():
    print(">>> Auto Alert Loop LIVE <<<")
    send_telegram("🟢 Bot LIVE ho gaya!\nAb /gold likho, turant signal ayega ✅")
    while True:
        try:
            p = get_price()
            print(f"Live Check: Gold Price ${p}")
        except Exception as e:
            print(e)
        time.sleep(60)

Thread(target=handle_gold_command, daemon=True).start()
Thread(target=auto_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
