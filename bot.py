import asyncio
from flask import Flask, request

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TOKEN
from handlers.commands import start, help_command
from handlers.messages import handle_message

app_flask = Flask(__name__)

# создаём Telegram приложение
tg_app = ApplicationBuilder().token(TOKEN).build()

# регистрируем handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

loop.run_until_complete(tg_app.initialize())
loop.run_until_complete(tg_app.start())

# Flask routes
@app_flask.route("/")
def home():
    return "Bot is running!"

@app_flask.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    try:
        print("🔥 WEBHOOK HIT")
        
        data = request.get_json(force=True)
        update = Update.de_json(data, tg_app.bot)

        loop.run_until_complete(tg_app.process_update(update))

        return "ok", 200

    except Exception as e:
        print("❌ ERROR:", e)
        return "error", 200

# запуск
if __name__ == "__main__":
    import os

    print("Starting bot...")

    PORT = int(os.getenv("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=PORT)