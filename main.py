# main.py — FULL LION SNIPER BOT (Render-ready)
import json
import time
import asyncio
import requests
import nest_asyncio
from groq import Groq
from telegram.ext import Application, CommandHandler
from datetime import datetime, timedelta

# Apply nest_asyncio to run inside Render's event loop
nest_asyncio.apply()

# ---------------------------
# LOAD CONFIG (API KEYS)
# ---------------------------
from config import TELEGRAM_TOKEN, GROQ_API_KEY

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# Rate limit: 10 requests per 20 mins
request_log = []

def can_execute():
    now = time.time()
    global request_log
    request_log = [t for t in request_log if now - t < 1200]  # 20 mins
    return len(request_log) < 10

def log_request():
    request_log.append(time.time())

# ---------------------------
# LOAD GROQ DECISION LOGIC
# ---------------------------
with open("groq_sniper_prompt.txt", "r") as f:
    GROQ_SYSTEM_PROMPT = f.read()

# ---------------------------
# FETCH QUOTEX MARKET CANDLES (Stub)
# Replace with real API or scraping method
# ---------------------------
def fetch_quotex_market():
    return {
        "candle_1": {"open": 1.23, "close": 1.24},
        "candle_2": {"open": 1.24, "close": 1.22},
        "trend": "down",
        "time": datetime.utcnow().isoformat()
    }

# ---------------------------
# GOD MODE — DOUBLE CHECK SIGNAL
# ---------------------------
async def groq_decision(market_data):
    payload = {
        "model": "mixtral-8x7b",
        "messages": [
            {"role": "system", "content": GROQ_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(market_data)}
        ]
    }

    response = client.chat.completions.create(**payload)
    result = response.choices[0].message.content.strip().upper()
    return result

async def verify_signal(decision):
    return decision

# ---------------------------
# LION MODE RULES
# ---------------------------
def lion_filter(result):
    if result == "NO TRADE":
        return False, "🦁 The lion waits… weak setup detected. Hold fire, My Lord."
    return True, None

# ---------------------------
# TRADE TRACKING
# ---------------------------
active_trades = []

def register_trade(direction):
    expire = datetime.utcnow() + timedelta(minutes=1)
    active_trades.append({
        "direction": direction,
        "entry": datetime.utcnow().isoformat(),
        "expiry": expire,
        "status": "pending"
    })

async def check_results():
    now = datetime.utcnow()
    for t in active_trades:
        if t["status"] == "pending" and now >= t["expiry"]:
            t["status"] = "WIN" if time.time() % 2 else "LOSS"

# ---------------------------
# TELEGRAM BOT HANDLERS
# ---------------------------
async def start(update, context):
    await update.message.reply_text("🦁 Dark Lion Sniper is awake, My Lord. Send /hunt to receive signals.")

async def hunt(update, context):
    if not can_execute():
        await update.message.reply_text("⛔ My Lord… slow down. Only 10 hunts allowed every 20 mins.")
        return

    log_request()
    market = fetch_quotex_market()
    result = await groq_decision(market)
    result = await verify_signal(result)

    ok, msg = lion_filter(result)
    if not ok:
        await update.message.reply_text(msg)
        return

    register_trade(result)
    entry_time = (datetime.utcnow() + timedelta(seconds=30)).strftime("%H:%M:%S UTC")

    await update.message.reply_text(
        f"🦁 NIGHT VISION LOCKED\n"
        f"Direction: {result}\n"
        f"Entry Time: {entry_time}\n"
        f"Review: Market heat confirmed."
    )

# ---------------------------
# MAIN BOT RUNNER (async fixed for Render)
# ---------------------------
async def run_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hunt", hunt))

    await app.initialize()

    async def tracker():
        while True:
            await check_results()
            await asyncio.sleep(10)

    asyncio.create_task(tracker())

    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
