from telegram import Update
from telegram.ext import ContextTypes

# AI pipeline
from core.prompt_builder import create_prompt
from services.ai_service import analyze_with_ai
# форматирование ответа
from utils.formatter import format_response
# UI (кнопки Telegram)
from handlers.keyboards import get_main_keyboard, get_number_keyboard
# работа с памятью пользователя
from state.user_state import set_user, get_user, add_message, get_history, clear_history

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): # вызывается на каждое текстовое сообщение
    user_id = update.effective_user.id
    text = update.message.text

    # обработка кнопок
    if text == "📊 Общий анализ":
        set_user(user_id, {"mode": "analysis", "top_n": 10, "freq_n": 10}) # сохраняем состояние пользователя
        await update.message.reply_text("Режим: общий анализ 📊\n\nОтправьте текст", reply_markup=get_main_keyboard()) # отвечаем пользователю
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
    
    elif text == "📜 Показать память":
        history = get_history(user_id)

        if not history:
            await update.message.reply_text("Память пустая")
            return

        text_history = "\n\n".join(
            f"{m['role']}: {m['content'][:100]}"
            for m in history
        )

        await update.message.reply_text(f"📜 История:\n\n{text_history}")
        return
    
    elif text == "🧹 Очистить память":
        clear_history(user_id)
        await update.message.reply_text(
            "Память очищена ✅\n\nВыберите режим 👇",
            reply_markup=get_main_keyboard()
        )
        return

    state = get_user(user_id) # получаем состояние пользователя

    if not state: # fallback (дефолтное состояние)
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

    mode = state.get("mode", "analysis") # получаем режим

    await update.message.reply_text("⏳ Анализирую текст...")

    prompt = create_prompt(
        text,
        mode,
        top_n=state.get("top_n", 10),
        freq_n=state.get("freq_n", 10)
    )

    add_message(user_id, "user", text)

    history = get_history(user_id)
    print("HISTORY:", get_history(user_id))

    messages = [
        {"role": "system", "content": prompt}
    ] + history

    try:
        ai_result = await analyze_with_ai(messages)
        add_message(user_id, "assistant", ai_result)

        result = format_response(ai_result, mode)

    except Exception as e:
        print("AI ERROR:", e)
        result = "❌ Ошибка при обработке. Попробуйте позже."

    await update.message.reply_text(
        result,
        reply_markup=get_main_keyboard()
    ) # отправляем результат и показываем меню