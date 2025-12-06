
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request
from config import TELEGRAM_TOKEN

app = Flask(__name__)

# -------------------
# TELEGRAM BOT HANDLERS
# -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦁 DARK TONY BUSINESS BOT ACTIVE.\nUse /signal ASSET TIMEFRAME"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Example sniper signal — replace with your Groq analysis later
    asset = context.args[0] if len(context.args) > 0 else "EURUSD"
    timeframe = context.args[1] if len(context.args) > 1 else "1m"
    await update.message.reply_text(
        f"🦁 SNIPER SIGNAL\nAsset: {asset}\nTimeframe: {timeframe}\nConfidence: 95%"
    )

# -------------------
# CREATE TELEGRAM APP
# -------------------
telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("signal", signal))

# -------------------
# FLASK WEBHOOK ROUTE
# -------------------
@app.route("/", methods=["POST"])
def webhook():
    telegram_app.update_queue.put_nowait(request.get_json(force=True))
    return "OK", 200

# -------------------
# FLASK ROOT TEST
# -------------------
@app.route("/", methods=["GET"])
def root():
    return "DARK TONY BOT ONLINE", 200
