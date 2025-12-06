
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from groq import Groq

# Load keys from config.py
from config import TELEGRAM_TOKEN, GROQ_API_KEY

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

async def start(update, context):
    await update.message.reply_text(
        "Your sniper is awake, locked in, and ready."
    )

async def handle_message(update, context):
    user_text = update.message.text

    try:
        # GROQ LLM Request
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": user_text}]
        )

        bot_reply = response.choices[0].message["content"]
        await update.message.reply_text(bot_reply)

    except Exception as e:
        await update.message.reply_text("System jammed. Check logs.")
        print("Error:", e)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot live. Sniper perched.")
    app.run_polling()


if __name__ == "__main__":
    main()
