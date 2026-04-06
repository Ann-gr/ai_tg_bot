import asyncio # нужен, потому что библиотека Telegram асинхронная
from flask import Flask, request

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import TOKEN
from handlers.commands import start, debug
from handlers.messages import handle_message, handle_document
from handlers.callbacks import handle_callback, debug_callbacks
from handlers.debug import debug_menu
from handlers.test_db import test_db

from services.db import connect_db
from state.db.init_db import init_db

# создаём веб-сервер
app_flask = Flask(__name__)

# создаём объект бота
tg_app = ApplicationBuilder().token(TOKEN).build()

# регистрируем handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("debug", debug_menu))
tg_app.add_handler(CommandHandler("testdb", test_db))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) # указываем, что нужно обрабатывать текст, но не команды
tg_app.add_handler(MessageHandler(filters.Document.ALL, handle_document)) # добавляем загрузку документов
tg_app.add_handler(CallbackQueryHandler(handle_callback)) # добавляем обработку callback-запросов
tg_app.add_handler(CallbackQueryHandler(debug_callbacks))
# создаём event loop вручную
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
init_db()
loop.run_until_complete(connect_db())

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