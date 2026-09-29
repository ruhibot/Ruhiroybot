import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.8-flash")

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
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception:
        await update.message.reply_text("দুঃখিত 😔 এখন উত্তর দিতে পারছি না।")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("Ruhi AI Bot is online!")
app.run_polling()
