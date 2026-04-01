import asyncio # нужен, потому что библиотека Telegram асинхронная
from flask import Flask, request

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TOKEN
from handlers.commands import start, help_command
from handlers.messages import handle_message

# создаём веб-сервер
app_flask = Flask(__name__)

# создаём объект бота
tg_app = ApplicationBuilder().token(TOKEN).build()

# регистрируем handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) # указываем, что нужно обрабатывать текст, но не команды

# создаём event loop вручную
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# запускаем Telegram приложение
loop.run_until_complete(tg_app.initialize())
loop.run_until_complete(tg_app.start())

# Flask routes
# проверка жив ли сервер, нужна для Render
@app_flask.route("/")
def home():
    return "Bot is running!"

@app_flask.route(f"/webhook/{TOKEN}", methods=["POST"]) # это URL, куда Telegram шлёт сообщения
def webhook():
    try:
        print("🔥 WEBHOOK HIT")
        
        data = request.get_json(force=True) # получаем JSON от Telegram
        update = Update.de_json(data, tg_app.bot) # превращаем JSON в объект Update

        loop.run_until_complete(tg_app.process_update(update))

        return "ok", 200

    except Exception as e:
        print("❌ ERROR:", e)
        return "error", 200

# запуск
if __name__ == "__main__": # точка входа
    import os

    print("Starting bot...")

    PORT = int(os.getenv("PORT", 10000)) # Render даёт порт через env
    app_flask.run(host="0.0.0.0", port=PORT) # запускаем сервер