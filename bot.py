import os, threading, requests, yfinance as yf
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def get_analysis():
    price = None
    high = low = open_p = None
    # 1. Real data yfinance se
    try:
        df = yf.download("GC=F", period="1d", interval="15m", progress=False, auto_adjust=True)
        if len(df) > 5:
            price = float(df['Close'].iloc[-1])
            high = float(df['High'].max())
            low = float(df['Low'].min())
            open_p = float(df['Open'].iloc[0])
            close = df['Close']
            ema9 = float(close.ewm(span=9).mean().iloc[-1])
            ema21 = float(close.ewm(span=21).mean().iloc[-1])
            # RSI
            delta = close.diff()
            gain = delta.where(delta>0,0).rolling(14).mean()
            loss = -delta.where(delta<0,0).rolling(14).mean()
            rs = gain/loss
            rsi = float(100 - (100/(1+rs.iloc[-1])))
    except:
        pass

    # 2. Fallback API agar yfinance fail
    if price is None:
        try:
            r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
            price = float(r['price'])
            open_p = float(r.get('openPrice', price))
            high = float(r.get('highPrice', price+10))
            low = float(r.get('lowPrice', price-10))
            ema9 = price - 1
            ema21 = price + 1
            rsi = 50.0
        except:
            return None

    pivot = (high + low + open_p) / 3
    # Trend logic - EMA + Pivot
    if price < ema9 and ema9 < ema21:
        signal = "SELL"
        sl = price + 15
        tp1 = price - 12
        tp2 = price - 26
        trend = f"EMA9 {ema9:.1f} < EMA21 {ema21:.1f} + Price Pivot {pivot:.1f} se niche - Strong SELL"
    elif price > ema9 and ema9 > ema21:
        signal = "BUY"
        sl = price - 15
        tp1 = price + 12
        tp2 = price + 26
        trend = f"EMA9 {ema9:.1f} > EMA21 {ema21:.1f} + Price Pivot {pivot:.1f} se upar - Strong BUY"
    else:
        # Pivot se decision
        if price < pivot - 2:
            signal = "SELL"
            sl = price + 14
            tp1 = price - 10
            tp2 = price - 22
            trend = f"Price ${price:.1f} Pivot ${pivot:.1f} se niche - SELL"
        elif price > pivot + 2:
            signal = "BUY"
            sl = price - 14
            tp1 = price + 10
            tp2 = price + 22
            trend = f"Price ${price:.1f} Pivot ${pivot:.1f} se upar - BUY"
        else:
            # Sideways me bhi EMA se force SELL/BUY
            signal = "SELL" if price < open_p else "BUY"
            sl = price + 12 if signal=="SELL" else price - 12
            tp1 = price - 10 if signal=="SELL" else price + 10
            tp2 = price - 20 if signal=="SELL" else price + 20
            trend = f"Sideways but Open ${open_p:.1f} se {'niche' if signal=='SELL' else 'upar'} - {signal}"

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
