from telegram import Update
from telegram.ext import ContextTypes
from handlers.keyboards import get_empty_keyboard
from state import state_manager

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = await state_manager.get_state(user_id)
    has_text = bool(state.get("last_text"))

    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я бот для анализа текста и документов.\n\n"
        "📂 Отправьте текст/файл\n"
        "или выберите действие ниже 👇",
        reply_markup=get_empty_keyboard()
    )