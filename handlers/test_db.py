from telegram import Update
from telegram.ext import ContextTypes

from services.db import get_pool

async def test_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pool = await get_pool()

        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")

        await update.message.reply_text(f"✅ DB OK: {result}")

    except Exception as e:
        await update.message.reply_text(f"❌ DB ERROR:\n{e}")