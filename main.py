
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
from groq import Groq

# ========================
# Load Keys from config.py
# ========================
from config import TELEGRAM_TOKEN, GROQ_API_KEY

bot = Bot(token=TELEGRAM_TOKEN)

# GROQ Client
groq_client = Groq(api_key=GROQ_API_KEY)

# Flask App (Render Webhook Host)
app = Flask(__name__)

# ========================
# SNIPER BUSINESS RULES
# ========================
SNIPER_RULES = """
You are DARK TONY SNIPER BOT.
You analyze financial charts with extreme precision.

RULES:
- Be short, direct, and strictly business-like.
- No jokes, no feelings, no emojis.
- Give only the final signal, not stories.
- Structure:
  1. Market Overview
  2. Direction (CALL/PUT)
  3. Entry Zone
  4. Confidence Level (0-100%)
  5. Warning if market unstable.
"""

# ==========
# GROQ LOGIC
# ==========
async def generate_signal(asset, timeframe):
    prompt = f"""
{SNIPER_RULES}

Analyze:
Asset: {asset}
Timeframe: {timeframe}

Return a signal following the rules.
"""

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]


# =====================
# COMMAND: /start
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "DARK TONY BUSINESS BOT ACTIVE.\nUse: /signal ASSET TIMEFRAME"
    )

# =====================
# COMMAND: /signal
# =====================
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        asset = context.args[0]
        timeframe = context.args[1]
    except:
        await update.message.reply_text("Format: /signal EURUSD 1m")
        return

    await update.message.reply_text("Processing…")

    result = await generate_signal(asset, timeframe)
    await update.message.reply_text(result)


# ================
# TELEGRAM WEBHOOK
# ================
async def telegram_process(update_json):
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signal", signal))

    update = Update.de_json(update_json, bot)
    await application.initialize()
    await application.process_update(update)
    return "ok"

# ==========
# FLASK ROUTE
# ==========
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        update_data = request.get_json(force=True)
        asyncio.run(telegram_process(update_data))
        return "OK", 200
    return "Bot active", 200


# ==========
# RUN FLASK
# ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
