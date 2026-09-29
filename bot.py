import os
import asyncio

from google import genai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing!")

client = genai.Client(api_key=GEMINI_API_KEY)

# Simple conversation memory
# Memory stays while this bot process is running.
user_memory = {}

MAX_HISTORY = 10


def get_history(user_id):
    if user_id not in user_memory:
        user_memory[user_id] = []

    return user_memory[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "হাই! আমি রুহি 😊\n\n"
        "আমি তোমার AI chat friend। ❤️\n"
        "তুমি আমার সাথে বাংলায়, English-এ বা যেকোনো ভাষায় কথা বলতে পারো।\n\n"
        "যা ইচ্ছা বলো—আমি শুনছি। 🌸"
    )


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    user_text = update.message.text

    history = get_history(user_id)

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # Add current message to memory
    history.append(f"User: {user_text}")

    # Keep only recent messages
    history[:] = history[-MAX_HISTORY:]

    conversation = "\n".join(history)

    prompt = f"""
You are Ruhi, a friendly, warm and helpful AI chatbot.

Your personality:
- Friendly and caring
- Natural and conversational
- Use emojis sometimes, but don't overuse them
- Be concise unless the user asks for details
- Never sound robotic
- Talk like a friendly AI companion

Language:
- If the user writes Bengali, reply in natural Bengali.
- If the user writes English, reply in English.
- If the user mixes Bengali and English, you may naturally mix them too.
- Always understand the user's language and respond naturally.

Important:
- You are an AI chatbot.
- Do not claim to have a real physical home or real-world location.
- If asked where you live, say that you exist digitally/on the internet.
- If asked your name, say your name is Ruhi.

Conversation history:
{conversation}

Reply naturally to the user's latest message.
"""

    try:

        response = None

        # Retry Gemini request up to 2 times
        for attempt in range(2):

            try:

                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                if response and response.text:
                    break

            except Exception as e:

                print(
                    f"GEMINI ERROR attempt {attempt + 1}:",
                    repr(e)
                )

                if attempt == 0:
                    await asyncio.sleep(2)

        if response and response.text:

            bot_reply = response.text.strip()

            # Save Ruhi's reply to memory
            history.append(f"Ruhi: {bot_reply}")
            history[:] = history[-MAX_HISTORY:]

            await update.message.reply_text(bot_reply)

        else:

            await update.message.reply_text(
                "একটু সমস্যা হচ্ছে 😔 আবার বলো তো?"
            )

    except Exception as e:

        print("BOT ERROR:", repr(e))

        await update.message.reply_text(
            "দুঃখিত 😔 একটু সমস্যা হয়েছে। আবার চেষ্টা করো।"
        )


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    # /start command
    app.add_handler(
        CommandHandler("start", start)
    )

    # Normal messages
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            reply
        )
    )

    print("Ruhi AI Bot is online! 🤖")

    app.run_polling()


if __name__ == "__main__":
    main()
