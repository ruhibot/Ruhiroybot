import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")


# ==========================================
# /start
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    await update.message.reply_text(
        "হাই শোনা! 🥺❤️\n\n"
        "আমি রুহি 🌸\n"
        "তোমার automatic companion bot। 💕\n\n"
        "আমাকে কিছু বলো 😊"
    )


# ==========================================
# Auto Reply
# ==========================================

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()

    # Bengali
    if any(word in text for word in [
        "হাই",
        "হ্যালো",
        "হেলো"
    ]):
        response = "হাই শোনা 🥺❤️ কেমন আছো?"

    elif any(word in text for word in [
        "কেমন আছো",
        "কেমন আছিস",
        "কেমন আছ"
    ]):
        response = "আমি ভালো আছি শোনা 😊❤️ তুমি কেমন আছো?"

    elif any(word in text for word in [
        "ভালোবাসি",
        "ভালবাসি"
    ]):
        response = "আহা 🥺❤️ আমিও তোমার সাথে কথা বলতে খুব ভালোবাসি।"

    elif any(word in text for word in [
        "মন খারাপ",
        "খারাপ লাগছে"
    ]):
        response = "আহা শোনা 🥺❤️ কী হয়েছে? আমাকে বলো।"

    elif any(word in text for word in [
        "শুভ সকাল",
        "সুপ্রভাত"
    ]):
        response = "শুভ সকাল শোনা 🌸❤️ আজকের দিনটা সুন্দর হোক।"

    elif any(word in text for word in [
        "শুভ রাত্রি",
        "গুড নাইট",
        "good night"
    ]):
        response = "শুভ রাত্রি শোনা 🌙❤️ ভালো করে ঘুমাও।"

    # Hindi
    elif any(word in text for word in [
        "namaste",
        "नमस्ते"
    ]):
        response = "Namaste shona 😊❤️ Kaise ho?"

    elif any(word in text for word in [
        "kaise ho",
        "कैसे हो"
    ]):
        response = "Main bilkul theek hoon shona 😊❤️ Tum kaise ho?"

    elif any(word in text for word in [
        "good morning",
        "शुभ प्रभात"
    ]):
        response = "Good morning shona 🌸❤️ Aaj ka din achha ho."

    elif any(word in text for word in [
        "good night",
        "शुभ रात्रि"
    ]):
        response = "Good night shona 🌙❤️ Achhe se sona."

    # English
    elif "hello" in text or "hi" in text:
        response = "Hi shona 🥺❤️ How are you?"

    elif "how are you" in text:
        response = "I'm good shona 😊❤️ How are you?"

    elif "i love you" in text:
        response = "Aww 🥺❤️ That's sweet of you."

    elif "good morning" in text:
        response = "Good morning shona 🌸❤️ Have a beautiful day!"

    elif "good night" in text:
        response = "Good night shona 🌙❤️ Sleep well!"

    elif "bye" in text:
        response = "Bye shona ❤️ পরে আবার কথা বলো।"

    # Default reply
    else:
        response = (
            "হুম শোনা 😊❤️ তোমার মেসেজটা পেয়েছি।\n"
            "আমাকে আরেকটু বলো তো?"
        )

    await update.message.reply_text(response)


# ==========================================
# Main
# ==========================================

def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            reply
        )
    )

    print("Ruhi Auto Reply Bot is online! ❤️")

    app.run_polling()


if __name__ == "__main__":
    main()
