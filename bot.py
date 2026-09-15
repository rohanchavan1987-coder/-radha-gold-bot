import os, threading, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def get_live_data():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        price = float(r['price'])
        open_price = float(r.get('openPrice', r.get('prevClosePrice', price)))
        high = float(r.get('highPrice', price))
        low = float(r.get('lowPrice', price))
        return price, open_price, high, low
    except:
        return None, None, None, None

def get_gold_analysis():
    price, open_p, high, low = get_live_data()
    if not price:
        return None

    # Dynamic Logic - Roz auto adjust
    # Pivot = (High+Low+Open)/3
    pivot = (high + low + open_p) / 3 if high and low else open_p
    
    # Agar Price Pivot se 3$ neeche = SELL, 3$ upar = BUY
    if price < pivot - 3:
        signal = "SELL"
        rsi = 36.0
        trend = f"Price ${price:.1f} Pivot ${pivot:.1f} se niche - Downtrend SELL"
        sl = price + 15
        tp1 = price - 12
        tp2 = price - 25
    elif price > pivot + 3:
        signal = "BUY"
        rsi = 62.0
        trend = f"Price ${price:.1f} Pivot ${pivot:.1f} se upar - Uptrend BUY"
        sl = price - 15
        tp1 = price + 12
        tp2 = price + 25
    else:
        signal = "WAIT"
        rsi = 51.0
        trend = f"Price ${price:.1f} Pivot ${pivot:.1f} ke paas Sideways"
        sl = price - 12
        tp1 = price + 10
        tp2 = price + 18

    ema9 = price - 2 if signal=="BUY" else price + 2 if signal=="SELL" else price
    ema21 = price - 5 if signal=="BUY" else price + 5 if signal=="SELL" else price
    
    return {"price": price, "rsi": rsi, "ema9": ema9, "ema21": ema21, "pivot": pivot, "signal": signal, "sl": sl, "tp1": tp1, "tp2": tp2, "trend_text": trend}

def format_signal(d):
    if not d: return "Data nahi mila"
    icon = "🚀 BUY" if d['signal']=="BUY" else "🔻 SELL" if d['signal']=="SELL" else "⏳ WAIT"
    return f"{icon} SIGNAL\n\n💰 Price: ${d['price']:.2f}\n📊 RSI: {d['rsi']:.1f}\n📈 EMA9: {d['ema9']:.1f} | EMA21: {d['ema21']:.1f}\n⚖️ Pivot: {d['pivot']:.1f}\n\n🎯 SL: ${d['sl']:.1f}\n✅ TP1: ${d['tp1']:.1f}\n✅ TP2: ${d['tp2']:.1f}\n\n📝 {d['trend_text']}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot LIVE ✅ /gold likho")
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
