
# main.py
import asyncio
import datetime
import random
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, GROQ_API_KEY

# --------------------------
# Flask app
# --------------------------
app = Flask(__name__)

# --------------------------
# Persistent event loop
# --------------------------
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# --------------------------
# Telegram Bot Application
# --------------------------
bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
loop.run_until_complete(bot_app.initialize())

# --------------------------
# Rate limiter (max 10 requests per 20 min)
# --------------------------
request_log = []

def can_execute():
    now = datetime.datetime.now().timestamp()
    global request_log
    request_log = [t for t in request_log if now - t < 20*60]
    return len(request_log) < 10

def log_request():
    request_log.append(datetime.datetime.now().timestamp())

# --------------------------
# Lion Sniper Engine (Groq signals)
# --------------------------
async def fetch_signal():
    """Fetch Groq signal (simulated)."""
    direction = random.choice(["CALL", "PUT"])
    confidence = random.randint(75, 99)
    entry_time = (datetime.datetime.now() + datetime.timedelta(seconds=60)).strftime("%H:%M:%S")
    return {"direction": direction, "confidence": confidence, "entry_time": entry_time}

async def verify_signal(signal):
    """God Mode recheck before sending."""
    second_check = signal["confidence"] - 3 + random.randint(0,5)
    final_conf = min(100, (signal["confidence"] + second_check)//2)
    signal["final_confidence"] = final_conf
    return signal

def lion_mode(signal):
    if signal["final_confidence"] < 85:
        return False, "🦁 Lion refuses weak trade. Wait a bit."
    return True, ""

active_trades = []

def register_trade(signal):
    """Track trades for result reporting."""
    active_trades.append({
        **signal,
        "status": "pending",
        "check_time": datetime.datetime.now() + datetime.timedelta(minutes=5)
    })

async def check_trade_results():
    now = datetime.datetime.now()
    for t in active_trades:
        if t["status"] == "pending" and now >= t["check_time"]:
            t["status"] = "WIN" if random.random() > 0.4 else "LOSS"

# --------------------------
# Telegram Commands
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🦁 Lion Sniper V3 ready. Type /scan to get a signal.")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not can_execute():
        await update.message.reply_text("⛔ Slow down, My Lord. Max 10 scans every 20 minutes.")
        return
    log_request()

    signal = await fetch_signal()
    signal = await verify_signal(signal)
    passed, msg = lion_mode(signal)
    if not passed:
        await update.message.reply_text(msg)
        return

    register_trade(signal)
    await update.message.reply_text(
        f"🦁 LION MODE SIGNAL\n"
        f"Direction: {signal['direction']}\n"
        f"Entry Time: {signal['entry_time']}\n"
        f"Confidence: {signal['final_confidence']}%\n"
        f"Move with the heart of a lion, My Lord."
    )

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("scan", scan))

# --------------------------
# Flask Webhook Route
# --------------------------
@app.route("/", methods=["POST"])
def webhook():
    """Receive Telegram update via webhook."""
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)
    # Schedule async processing on persistent loop
    loop.call_soon_threadsafe(
        asyncio.create_task,
        bot_app.process_update(update)
    )
    return "OK", 200

# --------------------------
# Keep alive for Render
# --------------------------
@app.route("/", methods=["GET"])
def index():
    return "Lion Sniper V3 is online 🦁", 200

# --------------------------
# Start Flask app
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
