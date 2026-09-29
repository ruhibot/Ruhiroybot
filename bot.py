import os
from google import genai

from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters


BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    prompt = f"""
You are Ruhi, a friendly AI Telegram chatbot.
Reply naturally and helpfully.
Use Bengali when the user writes Bengali.
Use the user's language when they use another language.

User message: {user_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        await update.message.reply_text(response.text)

    except Exception as e:
    print("GEMINI ERROR:", repr(e))
    await update.message.reply_text(
        "দুঃখিত 😔 এখন উত্তর দিতে পারছি না।"
    )
    
    
    
    = Application.builder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
)

print("Ruhi AI Bot is online!")

app.run_polling()
