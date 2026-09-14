import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Radha Gold Bot Live hai! /gold type karo")

# /gold command
async def gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gold: $2000 (Live Price)")

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("ERROR: BOT_TOKEN nahi mila!")
        return
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gold", gold))
    
    print("Bot started...")
    await app.run_polling()

# Render ko khush karne ke liye dummy server
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Running")
    print(f"Dummy server on port {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

if __name__ == "__main__":
    # Server ko background me chalao
    threading.Thread(target=run_dummy_server, daemon=True).start()
    asyncio.run(main())
