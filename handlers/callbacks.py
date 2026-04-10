from telegram import Update
from telegram.ext import ContextTypes

from handlers.keyboards import (
    get_mode_keyboard,
    get_param_keyboard,
    get_result_keyboard,
    get_main_menu_keyboard,
    get_back_keyboard,
)
from services.analysis_flow import process_user_input
from state import state_manager
from utils.text_utils import shorten_text
from utils.mode_utils import get_mode_title
from utils.params import build_params

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    state = await state_manager.get_state(user_id)

    data = query.data

    # UI навигация
    if data == "go:menu":
        await state_manager.update_state(user_id, **state)
        has_text = bool(state.get("last_text"))
        mode_title = get_mode_title(state.get("mode"))

        await query.edit_message_text(
            "📊 Главное меню\n\n"
            f"Текущий режим: {mode_title}\n\n"
            "Выберите действие:",
            reply_markup=get_main_menu_keyboard(state.get("mode"), has_text)
        )
        return

    elif data == "go:upload":
        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "📂 Отправьте текст или файл",
            reply_markup=get_back_keyboard()
        )
        return

    elif data == "go:help":
        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "🧠 *Режимы анализа*\n\n"
            "📊 *Общий анализ*\n"
            "→ краткое содержание, тема, ключевые идеи\n\n"
            "📝 *Краткое содержание*\n"
            "→ выжимка текста в 2–4 предложения\n\n"
            "🔑 *Ключевые слова*\n"
            "→ самые важные слова (вы выбираете количество)\n\n"
            "📈 *Частотный анализ*\n"
            "→ какие слова встречаются чаще всего\n\n"
            "🧠 *Тональность*\n"
            "→ позитивный / нейтральный / негативный\n\n"
            "❓ *Вопрос по тексту*\n"
            "→ вы можете хадать любой вопрос по тексту\n\n"
            "📌 Как это работает:\n"
            "1. Отправьте файл или текст\n"
            "2. Выберите режим\n"
            "3. Получите анализ\n"
            "4. При необходимости — измените режим без повторной загрузки",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
        return
    
    elif data == "go:example":
        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "📌 Пример работы:\n\n"
            "Вы отправляете:\n"
            "📄 PDF со статьёй\n\n"
            "Выбираете:\n"
            "📝 Краткое содержание\n\n"
            "Я возвращаю:\n"
            "• Основную мысль\n"
            "• Ключевые выводы\n"
            "• Короткое резюме",
            reply_markup=get_back_keyboard()
        )
        return

    if data.startswith("mode:"):
        mode = data.split(":")[1]
        state["mode"] = mode
        
        await state_manager.update_state(user_id, **state)

        if mode in ["keywords", "frequency"]:
            await query.edit_message_text(
                "Выберите количество:",
                reply_markup=get_param_keyboard(mode),
            )
            return
        
        if mode == "qa":
            await query.edit_message_text(
                "❓ Введите ваш вопрос по тексту:",
                reply_markup=get_back_keyboard(),
            )
            return

        await run_and_show_result(query, user_id, state)
        return

    if data.startswith("param:"):
        _, mode, value = data.split(":")
        state["mode"] = mode
        state["params"] = build_params(mode, value)
        await state_manager.update_state(user_id, **state)

        await run_and_show_result(query, user_id, state)
        return

    if data == "action:repeat":
        await run_and_show_result(query, user_id, state)
        return

    if data == "action:change_mode":
        await query.edit_message_text(
            "⚙️ Выберите новый режим анализа:",
            reply_markup=get_mode_keyboard(),
        )
        return

    if data == "action:new_text":
        state["last_text"] = None
        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "📂 Отправьте новый текст или файл", 
            reply_markup=get_back_keyboard())
        return
    
    if data == "action:full_result":
        full_text = state.get("last_result", "")

        if not full_text:
            await query.edit_message_text("❌ Нет результата")
            return
        
        title = get_mode_title(state.get("mode"))

        await query.edit_message_text(
            f"{title}\n\n{full_text}",
            reply_markup=get_result_keyboard(state.get("mode"), False),
        )
        return
    
    if data == "action:ask_more":
        state["mode"] = "qa"
        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "❓ Задайте следующий вопрос:", 
            reply_markup=get_back_keyboard())
        return
    
    if data == "action:qa_history":
        history = state.get("qa_history", [])[-5:]

        if not history:
            await query.edit_message_text(
                "❌ История пуста",
                reply_markup=get_back_keyboard())
            return

        text = "📜 История вопросов:\n\n"

        for item in history[-5:]:
            text += f"❓ {item['q']}\n"
            text += f"{item['a']}\n\n"

        await query.edit_message_text(
            text,
            reply_markup=get_back_keyboard()
        )
        return
    
    if data == "action:analysis_history":
        history = state.get("analysis_history", [])

        if not history:
            await query.edit_message_text(
                "❌ История анализов пуста",
                reply_markup=get_back_keyboard())
            return

        text = "📊 История анализов:\n\n"

        for item in history[-5:]:
            text += f"🔹 {item['mode']}\n"
            text += f"{item['result'][:200]}...\n\n"

        await query.edit_message_text(
            text,
            reply_markup=get_back_keyboard()
        )
        return

async def run_and_show_result(query, user_id, state):
    await query.edit_message_text("⏳ Анализирую...\n\nЭто может занять несколько секунд")

    data = await process_user_input(user_id, state)

    if data.get("error"):
        await query.edit_message_text(data["error"])
        return

    result = data["result"]

    state["last_result"] = result
    state["question"] = None
    await state_manager.update_state(user_id, **state)

    title = get_mode_title(state.get("mode"))
    short_text, is_truncated = shorten_text(result)

    formatted_text = (
        f"{title}\n\n"
        f"{short_text}\n\n"
    )

    if is_truncated:
        formatted_text += "👇 Нажмите, чтобы посмотреть полностью"

    await query.edit_message_text(
        formatted_text,
        reply_markup=get_result_keyboard(state.get("mode"), is_truncated),
    )