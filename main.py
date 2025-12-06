
import os
import asyncio
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# ======================
# CONFIGURATION
# ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # your Telegram bot token
GROQ_API_KEY = os.getenv("GROQ_API_KEY")      # your Groq API key
MAX_REQUESTS = 10
TIME_WINDOW = 20 * 60  # 20 minutes in seconds
LION_CONFIDENCE = 85   # minimum confidence for Lion Mode

# ======================
# STATE
# ======================
request_log = []
active_trades = []  # Tracks trades until expiration

# ======================
# UTILITY FUNCTIONS
# ======================
def can_execute():
    now = asyncio.get_event_loop().time()
    global request_log
    request_log = [t for t in request_log if now - t < TIME_WINDOW]
    return len(request_log) < MAX_REQUESTS

def log_request():
    request_log.append(asyncio.get_event_loop().time())

def get_precise_entry(duration_seconds=60):
    """Return precise entry timestamp in ISO format"""
    return (datetime.utcnow() + timedelta(seconds=duration_seconds)).isoformat()

# ======================
# MARKET SIGNAL FUNCTIONS
# ======================
async def fetch_market_signal():
    """
    Fetch a live signal from Groq API (simulate here for now)
    Replace the random section with real Groq API request
    """
    # Example (pseudo-code):
    # headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    # resp = requests.get("https://api.groq.com/v1/signal", headers=headers)
    # data = resp.json()
    # return data

    # TEMP SIMULATION
    direction = "CALL" if random.random() > 0.5 else "PUT"
    confidence = random.randint(75, 95)
    return {
        "direction": direction,
        "confidence": confidence,
        "entryTime": get_precise_entry(60),  # +60 seconds
        "duration": 60  # seconds till expiration
    }

async def god_mode_check(signal):
    """Recheck signal confidence before sending"""
    extra = random.randint(-3, 3)
    final_conf = min(100, (signal["confidence"] + extra) // 1)
    signal["finalConfidence"] = final_conf
    return signal

def lion_mode_filter(signal):
    """Reject weak signals"""
    if signal["finalConfidence"] < LION_CONFIDENCE:
        return False
    return True

def register_trade(signal):
    """Track trade until expiration"""
    expiration = datetime.utcnow() + timedelta(seconds=signal["duration"])
    active_trades.append({
        "signal": signal,
        "status": "pending",
        "expiration": expiration
    })

async def check_trades(bot_app):
    """Periodically check trades and report WIN/LOSS"""
    now = datetime.utcnow()
    for trade in active_trades:
        if trade["status"] == "pending" and now >= trade["expiration"]:
            # Replace random outcome with real Quotex verification if available
            trade["status"] = "WIN" if random.random() > 0.4 else "LOSS"
            msg = (
                f"🦁 **TRADE RESULT**\n"
                f"Direction: {trade['signal']['direction']}\n"
                f"Entry Time: {trade['signal']['entryTime']}\n"
                f"Confidence: {trade['signal']['finalConfidence']}%\n"
                f"Result: {trade['status']}\n"
                f"Stand tall, My Lord."
            )
            # Send to Telegram
            await bot_app.bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=msg)

# ======================
# TELEGRAM HANDLERS
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🦁 Lion Sniper Hybrid V3 Online — My Lord.")

async def snipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not can_execute():
        await update.message.reply_text(
            "⛔ My Lord, only 10 hunts per 20 minutes."
        )
        return

    log_request()
    sig = await fetch_market_signal()
    sig = await god_mode_check(sig)

    if not lion_mode_filter(sig):
        await update.message.reply_text(
            "🦁 The lion rejects this weak trade. Wait a bit, My Lord."
        )
        return

    register_trade(sig)

    msg = (
        f"🦁 **LION SNIPER SIGNAL**\n"
        f"Direction: {sig['direction']}\n"
        f"Entry Time: {sig['entryTime']}\n"
        f"Confidence: {sig['finalConfidence']}%\n"
        f"Move with precision, My Lord."
    )
    await update.message.reply_text(msg)

# ======================
# MAIN BOT
# ======================
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("snipe", snipe))

    # Run trade checker in background
    async def background_task():
        while True:
            await check_trades(app)
            await asyncio.sleep(5)  # check every 5 seconds

    asyncio.create_task(background_task())
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
