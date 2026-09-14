import os, requests, io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

def get_gold_data():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        price = float(r['price'])
        return price
    except:
        return 2000.0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🙏 Radha Gold Bot Live!\n/gold - Gold price dekhne ke liye")

async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_gold_data()
    await update.message.reply_text(f"✨ Gold Price: ${price:.2f}")

def main():
    if not TOKEN:
        print("BOT_TOKEN missing!")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
