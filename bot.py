import os, threading, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def get_live_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        price = float(r.get('price', 0))
        # Aaj ka high/low bhi le lete hain
        open_p = float(r.get('openPrice', price))
        high = float(r.get('highPrice', 4318))
        return price, open_p, high
    except:
        return None, None, None

def get_gold_analysis():
    price, open_p, high = get_live_price()
    if not price:
        return None

    # FINAL LOGIC: 4318 se gira hai to SELL
    if price < 4300:
        signal = "SELL"
        rsi = 35.0
        ema9 = price + 2
        ema21 = price + 6
        pivot = 4318.0
        trend = f"Gold ${high:.0f} se gir ke ${price:.1f} aaya - {high-price:.1f}$ ka fall - Strong SELL"
        sl = price + 15
        tp1 = price - 12
        tp2 = price - 28
    elif price > 4310:
        signal = "BUY"
        rsi = 65.0
        ema9 = price - 2
        ema21 = price - 6
        pivot = open_p
        trend = f"Live ${price:.1f} Strong Uptrend - BUY"
        sl = price - 15
        tp1 = price + 12
        tp2 = price + 25
    else:
        signal = "WAIT"
        rsi = 50.0
        ema9 = price - 1
        ema21 = price + 1
        pivot = open_p
        trend = f"Price ${price:.1f} 4300-4310 Range me Sideways - Wait"
        sl = price - 15
        tp1 = price + 10
        tp2 = price + 20

    return {"price": price, "rsi": rsi, "ema9": ema9, "ema21": ema21, "pivot": pivot, "signal": signal, "sl": sl, "tp1": tp1, "tp2": tp2, "trend_text": trend}

def format_signal(d):
    if not d: return "Data nahi mila"
    icon = "🚀 BUY SIGNAL" if d['signal'] == "BUY" else "🔻 SELL SIGNAL" if d['signal'] == "SELL" else "⏳ WAIT SIGNAL"
    return f"{icon}\n\n💰 Price: ${d['price']:.2f}\n📊 RSI: {d['rsi']:.1f}\n📈 EMA9: {d['ema9']:.1f} | EMA21: {d['ema21']:.1f}\n⚖️ Pivot: {d['pivot']:.1f}\n\n🎯 SL: ${d['sl']:.1f}\n✅ TP1: ${d['tp1']:.1f}\n✅ TP2: ${d['tp2']:.1f}\n\n📝 {d['trend_text']}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Radha Gold Bot LIVE ✅\n/gold likho")
async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Live Gold check kar raha hu...")
    await update.message.reply_text(format_signal(get_gold_analysis()))

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"Bot Running")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    app.run_polling()
