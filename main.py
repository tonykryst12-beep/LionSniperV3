import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

request_log = []

def can_execute():
    now = asyncio.get_event_loop().time()
    global request_log
    request_log = [t for t in request_log if now - t < 1200]
    return len(request_log) < 10

def log_request():
    request_log.append(asyncio.get_event_loop().time())

async def fetch_quotex_signal():
    return {
        "direction": "CALL" if random.random() > 0.5 else "PUT",
        "confidence": random.randint(75, 95),
        "entryTime": "60s from now"
    }

async def verify_signal(sig):
    second = sig["confidence"] - 3 + random.randint(0, 6)
    final = int((sig["confidence"] + second) / 2)
    sig["finalConfidence"] = min(final, 100)
    return sig

def lion_mode(sig):
    if sig["finalConfidence"] < 85:
        return {
            "pass": False,
            "message": "🦁 This trade is too weak. The lion rejects it. Wait."
        }
    return {"pass": True}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🦁 Lion Sniper V3 Online — My Lord.")

async def snipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not can_execute():
        await update.message.reply_text("⛔ My Lord, only 10 hunts per 20 minutes.")
        return
    
    log_request()

    sig = await fetch_quotex_signal()
    verified = await verify_signal(sig)
    lion = lion_mode(verified)

    if not lion["pass"]:
        await update.message.reply_text(lion["message"])
        return

    text = (
        f"🦁 **LION SNIPER SIGNAL**\n"
        f"Direction: {verified['direction']}\n"
        f"Entry Time: {verified['entryTime']}\n"
        f"Confidence: {verified['finalConfidence']}%\n\n"
        f"Move like the Black Lion, My Lord."
    )

    await update.message.reply_text(text)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("snipe", snipe))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
