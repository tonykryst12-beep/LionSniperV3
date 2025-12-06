# main.py — Lion Sniper Bot V3 (Render + Telegram Webhook)
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

# Import your keys from config.py
from config import TELEGRAM_TOKEN, GROQ_API_KEY

# -------------------- Setup --------------------
app = Flask(__name__)

# Initialize Telegram Application (async)
bot_app = Application.builder().token(TELEGRAM_TOKEN).build()

# Rate limiter
request_log = []
def can_execute():
    from time import time
    now = time()
    global request_log
    request_log = [t for t in request_log if now - t < 20 * 60]
    return len(request_log) < 10

def log_request():
    from time import time
    request_log.append(time())

# -------------------- Signal Logic --------------------
async def fetch_signal():
    """Fetch Groq/Quotex signal (mock or real analysis)."""
    import random, datetime
    return {
        "direction": "CALL" if random.random() > 0.5 else "PUT",
        "confidence": 75 + random.randint(0, 20),
        "entryTime": (datetime.datetime.utcnow() + datetime.timedelta(seconds=60)).isoformat()
    }

async def verify_signal(signal):
    """God mode confidence recheck."""
    second_check = signal["confidence"] - 3 + (random.randint(0, 5))
    signal["finalConfidence"] = min(100, (signal["confidence"] + second_check)//2)
    return signal

def lion_mode(signal):
    """Lion mode filter."""
    if signal["finalConfidence"] < 85:
        return False, "🦁 The lion refuses this weak trade. Wait a bit, hunter."
    return True, None

active_trades = []
def register_trade(signal):
    import time
    active_trades.append({
        **signal,
        "status": "pending",
        "checkTime": time.time() + 5*60
    })

async def check_trade_results():
    import time, random
    now = time.time()
    for t in active_trades:
        if t["status"] == "pending" and now >= t["checkTime"]:
            t["status"] = "WIN" if random.random() > 0.4 else "LOSS"

async def process_signal():
    if not can_execute():
        return "⛔ Slow down, My Lord. Lion only hunts 10 times every 20 minutes."
    log_request()
    sig = await fetch_signal()
    sig = await verify_signal(sig)
    passed, msg = lion_mode(sig)
    if not passed:
        return msg
    register_trade(sig)
    return f"""🦁 LION MODE SIGNAL
Direction: {sig['direction']}
Entry Time: {sig['entryTime']}
Confidence: {sig['finalConfidence']}%

Move with the heart of a lion, My Lord."""

# -------------------- Telegram Handlers --------------------
async def start(update: Update, context):
    await update.message.reply_text("🦁 Lion Sniper Bot Active. Send /signal to hunt.")

async def signal(update: Update, context):
    result = await process_signal()
    await update.message.reply_text(result)

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("signal", signal))

# -------------------- Flask Webhook --------------------
@app.route("/", methods=["POST"])
def webhook():
    """Receive Telegram update via webhook and process immediately."""
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)
    asyncio.create_task(bot_app.process_update(update))
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Lion Sniper Bot V3 Active", 200

# -------------------- Run Flask --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
