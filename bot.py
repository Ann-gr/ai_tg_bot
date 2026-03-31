from flask import Flask, request
from telegram import Update, Bot
from config import TOKEN
import os

app = Flask(__name__)
bot = Bot(TOKEN)


@app.route("/", methods=["GET"])
def home():
    return "Bot is running"


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, bot)

    print("🔥 UPDATE:", data)

    if update.message:
        text = update.message.text

        if text == "/start":
            bot.send_message(
                chat_id=update.message.chat.id,
                text="Бот работает 🚀"
            )
        else:
            bot.send_message(
                chat_id=update.message.chat.id,
                text=f"Ты написал: {text}"
            )

    return "ok"

if __name__ == "__main__":
    print("Starting bot...")

    PORT = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)