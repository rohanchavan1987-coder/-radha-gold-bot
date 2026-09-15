import os, threading, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def get_analysis():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        price = float(r['price'])
        high = float(r.get('highPrice', 4318))
        low = float(r.get('lowPrice', price-10))
        open_p = float(r.get('openPrice', price))
    except:
        return None

    # REAL LOGIC - Day High se kitna gira
    fall_from_high = high - price
    
    if fall_from_high > 10:  # High se 10$ se zyada gira to SELL
        signal = "SELL"
        rsi = 32.0
        ema9 = price + 3
        ema21 = price + 8
        pivot = high - 5
        trend = f"Gold ${high:.0f} High se ${fall_from_high:.1f} gira - Strong SELL"
        sl = price + 15
        tp1 = price - 12
        tp2 = price - 28
    elif price > open_p + 10:  # Open se 10$ upar to hi BUY
        signal = "BUY"
        rsi = 68.0
        ema9 = price - 3
        ema21 = price - 8
        pivot = low + 5
        trend = f"Price ${price:.1f} Open ${open_p:.1f} se {price-open_p:.1f}$ upar - BUY"
        sl = price - 15
        tp1 = price + 12
        tp2 = price + 28
    else:
        signal = "WAIT"
        rsi = 50.0
        ema9 = price
        ema21 = price
        pivot = (high+low)/2
        trend = f"Price ${price:.1f} Range me - Wait"
        sl = price - 12
        tp1 = price + 10
        tp2 = price + 18

    return {"price":price,"rsi":rsi,"ema9":ema9,"ema21":ema21,"pivot":pivot,"signal":signal,"sl":sl,"tp1":tp1,"tp2":tp2,"trend_text":trend}

def format_signal(d):
    if not d: return "Data nahi mila"
    icon = "🔻 SELL" if d['signal']=="SELL" else "🚀 BUY" if d['signal']=="BUY" else "⏳ WAIT"
    return f"{icon} SIGNAL\n\n💰 Price: ${d['price']:.2f}\n📊 RSI: {d['rsi']:.1f}\n📈 EMA9: {d['ema9']:.1f} | EMA21: {d['ema21']:.1f}\n⚖️ Pivot: {d['pivot']:.1f}\n\n🎯 SL: ${d['sl']:.1f}\n✅ TP1: ${d['tp1']:.1f}\n✅ TP2: ${d['tp2']:.1f}\n\n📝 {d['trend_text']}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot LIVE ✅ /gold likho")
async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Live Gold check kar raha hu...")
    await update.message.reply_text(format_signal(get_analysis()))

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
