from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TOKEN

app = Flask(__name__)

# Telegram app
tg_app = ApplicationBuilder().token(TOKEN).build()

# handlers
async def start(update, context):
    await update.message.reply_text("Бот работает 🚀")

async def echo(update, context):
    await update.message.reply_text(update.message.text)

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# webhook endpoint
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, tg_app.bot)

    # отправляем update в telegram app
    tg_app.create_task(tg_app.process_update(update))

    return "ok"

# health check для Render
@app.route("/", methods=["GET"])
def home():
    return "Bot is running"