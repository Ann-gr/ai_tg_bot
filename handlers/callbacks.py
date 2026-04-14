from telegram import Update
from telegram.ext import ContextTypes

from handlers.keyboards import (
    get_empty_keyboard,
    get_modes_keyboard,
    get_param_keyboard,
    get_result_keyboard,
    get_back_keyboard,
    get_analysis_history_keyboard,
    get_history_back_keyboard,
    get_qa_keyboard,
    get_history_menu
)
from services.analysis_flow import process_user_input
from state import state_manager
from state.state_manager import resolve_ui_state
from utils.text_utils import shorten_text
from utils.mode_utils import get_mode_title
from utils.params import build_params

def parse_callback(data: str):
    """
    Разбирает callback_data в action + payload
    """
    if ":" in data:
        action, *rest = data.split(":")
        return action, rest
    return data, []

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    state = await state_manager.get_state(user_id)

    action, payload = parse_callback(query.data)

    handler = ACTION_MAP.get(action)

    if not handler:
        await query.edit_message_text("❌ Неизвестное действие")
        return

    await handler(query, context, user_id, state, payload)

async def handle_go(query, context, user_id, state, payload):
    target = payload[0] if payload else None

    if target == "menu":
        await show_menu(query, state)

    elif target == "upload":
        await query.edit_message_text(
            "📂 Отправьте текст или файл",
            reply_markup=get_back_keyboard()
        )

    elif target == "help":
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
            "→ вы можете задать любой вопрос по тексту\n\n"
            "📌 Как это работает:\n"
            "1. Отправьте файл или текст\n"
            "2. Выберите режим\n"
            "3. Получите анализ\n"
            "4. При необходимости — измените режим без повторной загрузки",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    elif target == "history":
        await query.edit_message_text(
            "📜 История",
            reply_markup=get_history_menu()
        )

async def handle_mode(query, context, user_id, state, payload):
    mode = payload[0]
    state["mode"] = mode

    await state_manager.update_state(user_id, **state)

    if mode in ["keywords", "frequency"]:
        await query.edit_message_text(
            "Выберите количество:",
            reply_markup=get_param_keyboard(mode)
        )
        return

    if mode == "qa":
        state["ui_state"] = "QA"
        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "❓ Введите вопрос:",
            reply_markup=get_qa_keyboard()
        )
        return

    await run_and_show_result(query, user_id, state)

async def handle_param(query, context, user_id, state, payload):
    mode, value = payload

    state["mode"] = mode
    state["params"] = build_params(mode, value)

    await state_manager.update_state(user_id, **state)

    await run_and_show_result(query, user_id, state)

async def handle_action(query, context, user_id, state, payload):
    action = payload[0]

    if action == "repeat":
        await run_and_show_result(query, user_id, state)

    elif action == "new_text":
        state["last_text"] = None
        state["last_result"] = None

        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "📂 Отправьте новый текст",
            reply_markup=get_back_keyboard()
        )

    elif action == "change_mode":
        state["last_result"] = None
        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "🧠 Что вы хотите узнать из текста?",
            reply_markup=get_modes_keyboard()
        )

    elif action == "ask_more":
        state["mode"] = "qa"
        state["ui_state"] = "QA"

        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "❓ Напишите вопрос:",
            reply_markup=get_qa_keyboard()
        )

    elif action == "analysis_history":
        history = [
            x for x in state.get("analysis_history", [])
            if x.get("visible", True)
        ]

        if not history:
            await query.edit_message_text(
                "❌ История анализов пуста",
                reply_markup=get_back_keyboard()
            )
            return

        await query.edit_message_text(
            "📊 История анализов:",
            reply_markup=get_analysis_history_keyboard(history)
        )

    elif action == "qa_history":
        history = [
            x for x in state.get("qa_history", [])
            if x.get("visible", True)
        ]

        if not history:
            await query.edit_message_text(
                "❌ История вопросов пуста",
                reply_markup=get_back_keyboard()
            )
            return

        text = "📜 История вопросов:\n\n"

        for item in history[-5:]:
            text += f"❓ {item['q']}\n{item['a']}\n\n"

        await query.edit_message_text(
            text,
            reply_markup=get_history_back_keyboard()
        )

    elif action == "clear_all":
        for item in state.get("qa_history", []):
            item["visible"] = False

        for item in state.get("analysis_history", []):
            item["visible"] = False

        await state_manager.update_state(user_id, **state)

        await query.edit_message_text(
            "🧹 История очищена",
            reply_markup=get_back_keyboard()
        )

    elif action == "short_result":
        state["result_view"] = "short"
        await state_manager.update_state(user_id, **state)

        short_text, is_truncated = shorten_text(state.get("last_result"))

        title = get_mode_title(state.get("mode"))

        await query.edit_message_text(
            f"{title}\n\n{short_text}",
            reply_markup=get_result_keyboard("short", is_truncated),
        )

    elif action == "full_result":
        full_text = state.get("last_result")

        if not full_text:
            await query.edit_message_text(
                "❌ Нет результата",
                reply_markup=get_back_keyboard()
            )
            return
        
        state["result_view"] = "full"
        await state_manager.update_state(user_id, **state)

        title = get_mode_title(state.get("mode"))

        _, is_truncated = shorten_text(full_text)

        await query.edit_message_text(
            f"{title}\n\n{full_text}",
            reply_markup=get_result_keyboard("full", is_truncated),
        )

async def handle_analysis_item(query, context, user_id, state, payload):
    item_id = payload[0]

    history = state.get("analysis_history", [])

    item = next((x for x in history if x["id"] == item_id), None)

    if not item:
        await query.edit_message_text(
            "❌ Анализ не найден",
            reply_markup=get_back_keyboard()
        )
        return

    title = get_mode_title(item["mode"])

    await query.edit_message_text(
        f"{title}\n\n{item['result']}",
        reply_markup=get_history_back_keyboard()
    )

async def show_menu(query, state):
    ui = state.get("ui_state") or resolve_ui_state(state)

    if ui == "EMPTY":
        await query.edit_message_text(
            "📂 Отправьте текст",
            reply_markup=get_empty_keyboard()
        )

    elif ui == "TEXT_LOADED":
        await query.edit_message_text(
            "🧠 Что вы хотите узнать из текста?",
            reply_markup=get_modes_keyboard()
        )

    elif ui == "RESULT":
        await query.edit_message_text(
            "📊 Выберите действие:",
            reply_markup=get_result_keyboard()
        )

    elif ui == "QA":
        await query.edit_message_text(
            "❓ Задайте вопрос:",
            reply_markup=get_qa_keyboard()
        )

async def run_and_show_result(query, user_id, state):
    await query.edit_message_text("⏳ Анализирую...\n\nЭто может занять несколько секунд")

    data = await process_user_input(user_id, state)

    if data.get("error"):
        await query.edit_message_text(data["error"])
        return
    
    if data.get("action") != "show_result":
        await query.edit_message_text("❌ Не удалось выполнить анализ")
        return

    result = data["result"]

    state = data["state"]
    state["last_result"] = result
    state["question"] = None
    state["ui_state"] = "RESULT"
    state["result_view"] = "short"

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
        reply_markup=get_result_keyboard(state["result_view"], is_truncated),
    )

ACTION_MAP = {
    "go": handle_go,
    "mode": handle_mode,
    "param": handle_param,
    "action": handle_action,
    "analysis_item": handle_analysis_item
}