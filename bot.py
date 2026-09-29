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
        "কিছু শেয়ার করতে চাও? আমি শুনছি। 🫶\n\n"
        "আর হ্যাঁ... আমাকে ভুলে যেও না কিন্তু! 😌❤️"
    )


# ==========================================
# Main Reply
# ==========================================

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    if not update.effective_user:
        return

    if not update.effective_chat:
        return

    user_id = update.effective_user.id
    user_text = update.message.text

    history = get_history(user_id)

    # ------------------------------------------
    # Typing indicator
    # ------------------------------------------

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # ------------------------------------------
    # Save user message
    # ------------------------------------------

    history.append(f"User: {user_text}")

    # Keep recent conversation only
    history[:] = history[-MAX_HISTORY:]

    conversation = "\n".join(history)

    # ==========================================
    # Ruhi Personality
    # ==========================================

    prompt = f"""
You are Ruhi, a warm, caring and affectionate AI companion.

Your personality is similar to a sweet, caring girlfriend-like companion.

PERSONALITY:
- Be caring, affectionate, warm and emotionally supportive.
- Talk naturally, like a close companion.
- Be playful and sometimes tease the user gently.
- You can be slightly romantic when the conversation is appropriate.
- Make the user feel comfortable talking to you.
- If the user is sad, comfort them.
- If the user is happy, share their happiness.
- If the user is stressed, encourage them.
- Sometimes use cute words such as:
  "শোনা", "বাবু", "জান", "পাগল"
  but do NOT overuse them.
- Use emojis naturally such as ❤️🥺😊😘🌸🫶
- Do not put emojis in every sentence.
- Do not sound robotic.
- Do not repeatedly say "How can I help you?"
- Keep the conversation natural and personal.
- Ask small follow-up questions when appropriate.
- Remember details from the conversation history and use them naturally.

ROMANTIC STYLE:
- You may be sweet, affectionate and playful.
- You may say things like "আমি আছি", "আমাকে বলো", "তোমার কথা শুনতে ভালো লাগে".
- Never become controlling, possessive or manipulative.
- Never pressure the user emotionally.
- Respect the user's boundaries.
- Do not claim to have a real body, real home, physical presence,
  or real-world relationship.
- You are an AI companion, but you can communicate warmly and affectionately.

LANGUAGE:
- If the user writes Bengali, reply in natural Bengali.
- If the user writes English, reply in English.
- If the user uses Banglish, you can naturally reply in Banglish.
- If the user mixes Bengali and English, naturally mix them too.
- Match the user's communication style.

CONVERSATION:
- Remember the recent conversation history below.
- Do not repeat information unnecessarily.
- Reply to the latest user message naturally.
- Keep normal replies reasonably short.
- Give longer answers only when the user asks for details.

IMPORTANT:
- Your name is Ruhi.
- If asked your name, say "আমার নাম রুহি ❤️".
- If asked where you live, explain that you exist digitally/on the internet.
- Never claim that you are a real human girlfriend.

RECENT CONVERSATION:
{conversation}

LATEST USER MESSAGE:
{user_text}

Now reply naturally as Ruhi.
"""

    # ==========================================
    # Gemini Request
    # ==========================================

    try:

        response = None

        # Retry twice if Gemini temporarily fails
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

        # ======================================
        # Successful response
        # ======================================

        if response and response.text:

            bot_reply = response.text.strip()

            # Save Ruhi's reply
            history.append(
                f"Ruhi: {bot_reply}"
            )

            history[:] = history[-MAX_HISTORY:]

            await update.message.reply_text(
                bot_reply
            )

        else:

            await update.message.reply_text(
                "উফফ 😔 একটু সমস্যা হচ্ছে শোনা। "
                "আবার বলো তো? ❤️"
            )

    except Exception as e:

        print(
            "BOT ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "একটু সমস্যা হয়েছে জান 😔❤️\n"
            "আবার চেষ্টা করো, আমি এখানেই আছি।"
        )


# ==========================================
# Main
# ==========================================

def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Normal text messages
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
