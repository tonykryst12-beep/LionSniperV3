import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # https://yourapp.onrender.com/webhook

bot = Bot(TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot, None, workers=0)

# --- Commands ---
def start(update, context):
    update.message.reply_text("🔥 Black Lion Sniper Online, My Lord.")

dispatcher.add_handler(CommandHandler("start", start))

# --- Webhook endpoint ---
@app.post("/webhook")
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return "OK", 200

# --- Root page ---
@app.get("/")
def home():
    return "Black Lion Sniper Active"

# --- Set Webhook once ---
if __name__ == "__main__":
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
