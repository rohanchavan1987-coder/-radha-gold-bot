import os, requests, io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")

def get_gold_data():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        price = float(r['price'])
    except:
        price = 4298.0
    pivot=4275.0
    if price>4280:
        signal,rsi,sl,tp1,tp2="BUY",68.0,price-18,price+12,price+25
        reason=f"Price {price:.1f} Pivot {pivot} se upar"
    elif price<4260:
        signal,rsi,sl,tp1,tp2="SELL",35.0,price+18,price-12,price-25
        reason=f"Price {price:.1f} Pivot {pivot} se niche"
    else:
        signal,rsi,sl,tp1,tp2="WAIT",52.0,price-10,price+10,price+20
        reason="Pivot ke aas paas"
    return price,rsi,price-5,price-12,pivot,signal,reason,sl,tp1,tp2

def make_chart(price,pivot,sl,tp1,tp2,signal):
    fig,ax=plt.subplots(figsize=(6,4))
    levels=[sl,pivot,price,tp1,tp2]
    for lvl in levels:
        ax.axhline(lvl, linestyle='--', linewidth=1)
    ax.set_title(f'XAUUSD {signal}')
    ax.set_ylim(min(levels)-10, max(levels)+10)
    buf=io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    plt.close()
    return buf

async def start(update, context):
    await update.message.reply_text("🔥 24x7 Online! /price /signal")

async def signal_cmd(update, context):
    price,rsi,ema9,ema21,pivot,signal,reason,sl,tp1,tp2=get_gold_data()
    chart=make_chart(price,pivot,sl,tp1,tp2,signal)
    msg=f"{signal} ${price:.2f}\nSL:{sl:.1f} TP1:{tp1:.1f} TP2:{tp2:.1f}\n{reason}"
    await update.message.reply_photo(photo=chart, caption=msg)

async def price_cmd(update, context):
    price,*_=get_gold_data()
    await update.message.reply_text(f"💰 ${price:.2f}")

app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price_cmd))
app.add_handler(CommandHandler("signal", signal_cmd))
app.run_polling()
