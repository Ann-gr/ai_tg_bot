from telegram import Update
from telegram.ext import ContextTypes

from core.prompt_builder import create_prompt
from services.ai_service import analyze_with_ai
from state.user_state import user_state
from utils.formatter import format_response
from handlers.keyboards import get_main_keyboard, get_number_keyboard
from state.user_state import get_user, set_user

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # обработка кнопок
    if text == "📊 Общий анализ":
        set_user(user_id, {"mode": "analysis", "top_n": 10, "freq_n": 10})
        await update.message.reply_text("Режим: общий анализ 📊\n\nОтправьте текст", reply_markup=get_main_keyboard())
        return

    elif text == "📝 Краткое содержание":
        set_user(user_id, {"mode": "summary", "top_n": 10, "freq_n": 10})
        await update.message.reply_text("Режим: краткое содержание 📝\n\nОтправьте текст", reply_markup=get_main_keyboard())
        return

    elif text == "🔑 Ключевые слова":
        set_user(user_id, {"mode": "keywords", "waiting_for_number": True})
        await update.message.reply_text("Сколько слов вывести?", reply_markup=get_number_keyboard())
        return

    elif text == "📈 Частотный анализ":
        set_user(user_id, {"mode": "frequency", "waiting_for_number": True})
        await update.message.reply_text("Сколько слов вывести?", reply_markup=get_number_keyboard())
        return
    
    elif text == "⬅️ Назад":
        await update.message.reply_text(
            "Выберите режим 👇",
            reply_markup=get_main_keyboard()
        )
        return

    state = get_user(user_id)

    if not state:
        state = {
            "mode": "analysis",
            "top_n": 10,
            "freq_n": 10
        }

    # если ждём число
    if state.get("waiting_for_number"):
        if text not in ["5", "10", "15", "20", "25", "30"]:
            await update.message.reply_text("Пожалуйста, выберите число кнопкой 👇")
            return

        number = int(text)

        if state["mode"] == "keywords":
            state["top_n"] = number
        elif state["mode"] == "frequency":
            state["freq_n"] = number

        state["waiting_for_number"] = False

        set_user(user_id, state)

        await update.message.reply_text(
            f"Отлично! Выбрано: {number} ✅\n\nТеперь отправьте текст", reply_markup=get_main_keyboard()
        )
        return

    mode = state.get("mode", "analysis")

    await update.message.reply_text("⏳ Анализирую текст...")

    prompt = create_prompt(
        text,
        mode,
        top_n=state.get("top_n", 10),
        freq_n=state.get("freq_n", 10)
    )

    result = format_response(analyze_with_ai(prompt), mode)

    await update.message.reply_text(
        result,
        reply_markup=get_main_keyboard()
    )