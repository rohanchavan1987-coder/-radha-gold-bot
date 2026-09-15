import os
import threading
import yfinance as yf
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def get_gold_analysis():
    try:
        data = yf.download("GC=F", period="2d", interval="5m", progress=False)
        if len(data) < 30:
            return None
        close = data['Close']
        high = data['High']
        low = data['Low']
        price = float(close.iloc[-1])
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = float(rsi.iloc[-1])
        ema9 = float(close.ewm(span=9, adjust=False).mean().iloc[-1])
        ema21 = float(close.ewm(span=21, adjust=False).mean().iloc[-1])
        prev_day = data.resample('D').agg({'High':'max','Low':'min','Close':'last'}).dropna()
        if len(prev_day) >= 1:
            h = float(prev_day['High'].iloc[-1]); l = float(prev_day['Low'].iloc[-1]); c = float(prev_day['Close'].iloc[-1])
            pivot = (h + l + c) / 3
        else:
            pivot = (float(high.iloc[-1]) + float(low.iloc[-1]) + float(close.iloc[-1])) / 3
        
        signal = "WAIT"
        if price > pivot and price > ema9 and ema9 > ema21 and rsi > 50 and rsi < 75:
            signal = "BUY"
        elif price < pivot and price < ema9 and ema9 < ema21 and rsi < 50 and rsi > 25:
            signal = "SELL"

        if signal == "BUY":
            sl = price - 18; tp1 = price + 12; tp2 = price + 25
            trend_text = f"Price {price:.1f} Pivot {pivot:.1f} se upar, Strong Uptrend"
        elif signal == "SELL":
            sl = price + 18; tp1 = price - 12; tp2 = price - 25
            trend_text = f"Price {price:.1f} Pivot {pivot:.1f} se niche, Strong Downtrend"
        else:
            sl = price - 15; tp1 = price + 10; tp2 = price + 20
            trend_text = f"Price {price:.1f} Pivot {pivot:.1f} ke aas paas, Sideways"

        return {"price": price, "rsi": rsi_val, "ema9": ema9, "ema21": ema21, "pivot": pivot, "signal": signal, "sl": sl, "tp1": tp1, "tp2": tp2, "trend_text": trend_text}
    except Exception as e:
        print(f"Error: {e}")
        return None

def format_signal(d):
    if not d: return "Gold data nahi mil raha, 1 min baad try karo."
    icon = "🚀 BUY SIGNAL" if d['signal'] == "BUY" else "🔻 SELL SIGNAL" if d['signal'] == "SELL" else "⏳ WAIT SIGNAL"
    return f"{icon}\n\n💰 Price: ${d['price']:.2f}\n📊 RSI: {d['rsi']:.1f}\n📈 EMA9: {d['ema9']:.1f} | EMA21: {d['ema21']:.1f}\n⚖️ Pivot: {d['pivot']:.1f}\n\n🎯 SL: ${d['sl']:.1f}\n✅ TP1: ${d['tp1']:.1f}\n✅ TP2: ${d['tp2']:.1f}\n\n📝 {d['trend_text']}\n\nRisk: 1:1.5"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Radha Gold Bot LIVE ✅\n/gold likho")

async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Live Gold check kar raha hu...")
    data = get_gold_analysis()
    await update.message.reply_text(format_signal(data))

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"Bot Running")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    print("Bot started with Real Gold Logic...")
    app.run_polling()
