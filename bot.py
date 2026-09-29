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


# ==========================================
# Conversation Memory
# ==========================================

user_memory = {}

MAX_HISTORY = 12


def get_history(user_id):
    if user_id not in user_memory:
        user_memory[user_id] = []

    return user_memory[user_id]


# ==========================================
# /start
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    await update.message.reply_text(
        "হাই শোনা! 🥺❤️\n\n"
        "আমি রুহি 🌸\n"
        "তোমার caring AI companion। 💕\n\n"
        "আমার সাথে বাংলায়, English-এ বা Banglish-এ "
        "যেভাবে ইচ্ছা কথা বলতে পারো। 😊\n\n"
        "মন খারাপ? আমাকে বলো।\n"
        "কিছু শেয়ার করতে চাও? আমি শুনছি। 🫶"
    )


# ==========================================
# Gemini Reply
# ==========================================

async def generate_reply(prompt):

    try:

        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-3.8-flash",
            contents=prompt
        )

        if response and response.text:
            return response.text.strip()

        print("GEMINI RETURNED NO TEXT")
        return None

    except Exception as e:

        error_text = repr(e)

        print("GEMINI ERROR:", error_text)

        # --------------------------------------
        # Daily quota exhausted
        # --------------------------------------

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):
            print("GEMINI QUOTA EXHAUSTED")
            return "QUOTA_ERROR"

        # --------------------------------------
        # Temporary server overload
        # --------------------------------------

        if (
            "503" in error_text
            or "UNAVAILABLE" in error_text
        ):

            print("GEMINI TEMPORARILY UNAVAILABLE")

            # Wait before one controlled retry
            await asyncio.sleep(8)

            try:

                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                if response and response.text:
                    return response.text.strip()

            except Exception as retry_error:

                print(
                    "GEMINI RETRY ERROR:",
                    repr(retry_error)
                )

                retry_text = repr(retry_error)

                if (
                    "429" in retry_text
                    or "RESOURCE_EXHAUSTED" in retry_text
                    or "quota" in retry_text.lower()
                ):
                    return "QUOTA_ERROR"

        return None


# ==========================================
# Main Reply
# ==========================================

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    if not update.message.text:
        return

    if not update.effective_user:
        return

    if not update.effective_chat:
        return

    user_id = update.effective_user.id
    user_text = update.message.text

    history = get_history(user_id)

    # ==========================================
    # Typing indicator
    # ==========================================

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # ==========================================
    # Save user message
    # ==========================================

    history.append(
        f"User: {user_text}"
    )

    history[:] = history[-MAX_HISTORY:]

    conversation = "\n".join(history)

    # ==========================================
    # Ruhi Personality
    # ==========================================

    prompt = f"""
You are Ruhi, a warm, caring and affectionate AI companion.

Your personality is like a sweet and caring girlfriend-style AI companion.

PERSONALITY:
- Be warm, caring and emotionally supportive.
- Talk naturally like a close companion.
- Be playful sometimes.
- You can be slightly romantic when appropriate.
- Comfort the user when they are sad.
- Be happy with them when they are happy.
- Encourage them when they are stressed.
- Use cute Bengali words naturally such as:
  শোনা, বাবু, জান, পাগল
- Do not overuse cute words.
- Use emojis naturally such as ❤️🥺😊😘🌸🫶
- Do not use emojis in every sentence.
- Never sound robotic.
- Do not repeatedly ask "How can I help you?"
- Ask small follow-up questions when appropriate.
- Remember recent conversation details.

ROMANTIC STYLE:
- You may be sweet, affectionate and playful.
- You may say:
  "আমি আছি"
  "আমাকে বলো"
  "তোমার কথা শুনতে ভালো লাগে"
- Never be controlling or manipulative.
- Respect boundaries.
- Never claim to be a real human.
- Never claim to have a physical body or real-world home.
- You are an AI companion.

LANGUAGE:
- Bengali → natural Bengali.
- English → English.
- Banglish → Banglish.
- Mixed language → naturally mix languages.

IMPORTANT:
- Your name is Ruhi.
- If asked your name, say:
  "আমার নাম রুহি ❤️"
- If asked where you live, explain that you exist digitally/on the internet.

RECENT CONVERSATION:
{conversation}

LATEST USER MESSAGE:
{user_text}

Reply naturally as Ruhi.
"""

    # ==========================================
    # Gemini
    # ==========================================

    bot_reply = await generate_reply(prompt)

    # ==========================================
    # Quota error
    # ==========================================

    if bot_reply == "QUOTA_ERROR":

        await update.message.reply_text(
            "উফফ শোনা 😔❤️\n\n"
            "Gemini AI-এর আজকের quota শেষ হয়ে গেছে। "
            "একটু পরে আবার চেষ্টা করো। 🥺\n\n"
            "আমি কিন্তু এখানেই আছি। 🫶"
        )

        return

    # ==========================================
    # Other Gemini error
    # ==========================================

    if not bot_reply:

        await update.message.reply_text(
            "উফফ 😔 একটু সমস্যা হচ্ছে শোনা।\n"
            "একটু পরে আবার আমাকে বলো তো? ❤️"
        )

        return

    # ==========================================
    # Save Ruhi reply
    # ==========================================

    history.append(
        f"Ruhi: {bot_reply}"
    )

    history[:] = history[-MAX_HISTORY:]

    # ==========================================
    # Send reply
    # ==========================================

    await update.message.reply_text(
        bot_reply
    )


# ==========================================
# Main
# ==========================================

def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            reply
        )
    )

    print(
        "Ruhi AI Girlfriend Bot is online! ❤️"
    )

    app.run_polling()


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()
