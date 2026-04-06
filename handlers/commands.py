from telegram import Update
from telegram.ext import ContextTypes
from handlers.keyboards import get_main_menu_keyboard
from state.db.debug import print_user
from state import state_manager

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я бот для анализа текста и документов.\n\n"
        "📂 Отправьте текст/файл\n"
        "или выберите действие ниже 👇",
        reply_markup=get_main_menu_keyboard(False)
    )

async def debug(update, context):
    user_id = update.effective_user.id

    state = state_manager.get_state(user_id)

    await update.message.reply_text(
        f"STATE:\n{state}"
    )