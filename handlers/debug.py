from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# /debug
async def debug_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 State", callback_data="debug_state")],
        [InlineKeyboardButton("💬 History", callback_data="debug_history")],
        [InlineKeyboardButton("🧾 Raw JSON", callback_data="debug_raw")],
        [InlineKeyboardButton("🧹 Clear history", callback_data="debug_clear")]
    ]

    await update.message.reply_text(
        "🛠 Debug menu:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )