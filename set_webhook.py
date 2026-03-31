import asyncio
from config import TOKEN
from telegram import Bot

URL = "https://ai-tg-bot-lf1m.onrender.com/webhook/" + TOKEN

async def main():
    bot = Bot(TOKEN)
    await bot.set_webhook(url=URL)
    print("Webhook set!")

asyncio.run(main())