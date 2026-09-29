import os

from google import genai
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    prompt = f"""
You are Ruhi, a friendly AI Telegram chatbot.

Reply naturally and helpfully.

If the user writes in Bengali, reply in Bengali.
If the user writes in English, reply in English.
If the user uses another language, reply in that language.

Keep replies friendly and easy to understand.

User message:
{user_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text(
                "দুঃখিত 😔 কোনো উত্তর পাওয়া যায়নি।"
            )

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        await update.message.reply_text(
            "দুঃখিত 😔 এখন উত্তর দিতে পারছি না।"
        )


def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            reply
        )
    )

    print("Ruhi AI Bot is online!")

    app.run_polling()


if __name__ == "__main__":
    main()
