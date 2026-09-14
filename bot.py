import os, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

def get_gold_data():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        return float(r['price'])
    except:
        return 2000.0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🙏 Radha Gold Bot Live!\n/gold likho gold price ke liye")

async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_gold_data()
    await update.message.reply_text(f"✨ Gold: ${price:.2f}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    app.run_polling()

if __name__ == "__main__":
    main()
