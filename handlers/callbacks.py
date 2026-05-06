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
from services.history_repository import get_user_analysis, hide_all_analysis, get_analysis_by_id_for_user, get_user_qa, hide_all_qa
from services.analysis_flow import run_analysis_pipeline
from state import state_manager
from state.state_manager import resolve_ui_state
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
        await query.message.reply_text("❌ Неизвестное действие")
        return

    await handler(query, context, user_id, state, payload)

async def handle_go(query, context, user_id, state, payload):
    target = payload[0] if payload else None

    if target == "menu":
        await show_menu(query, state)

    elif target == "upload":
        await query.message.reply_text(
            "📂 Отправьте текст или файл",
            reply_markup=get_back_keyboard()
        )

    elif target == "help":
        await query.message.reply_text(
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
        await query.message.reply_text(
            "📜 История",
            reply_markup=get_history_menu()
        )

async def handle_mode(query, context, user_id, state, payload):
    mode = payload[0]
    state["mode"] = mode

    await state_manager.update_state(user_id, **state)

    if mode in ["keywords", "frequency"]:
        await query.message.reply_text(
            "Выберите количество:",
            reply_markup=get_param_keyboard(mode)
        )
        return

    if mode == "qa":
        state["ui_state"] = "QA"
        await state_manager.update_state(user_id, **state)

        await query.message.reply_text(
            "❓ Введите вопрос:",
            reply_markup=get_qa_keyboard()
        )
        return

    await run_analysis_pipeline(
        send_func=query.message.reply_text,
        user_id=user_id,
        state=state
    )

async def handle_param(query, context, user_id, state, payload):
    mode, value = payload

    state["mode"] = mode
    state["params"] = build_params(mode, value)

    await state_manager.update_state(user_id, **state)

    await run_analysis_pipeline(
        send_func=query.message.reply_text,
        user_id=user_id,
        state=state
    )

async def handle_action(query, context, user_id, state, payload):
    action = payload[0]

    if action == "repeat":
        await run_analysis_pipeline(
            send_func=query.message.reply_text,
            user_id=user_id,
            state=state
        )

    elif action == "new_text":
        await state_manager.update_state(user_id, **state)

        await query.message.reply_text(
            "📂 Отправьте новый текст",
            reply_markup=get_back_keyboard()
        )

    elif action == "change_mode":
        await state_manager.update_state(user_id, **state)

        await query.message.reply_text(
            "🧠 Что вы хотите узнать из текста?",
            reply_markup=get_modes_keyboard()
        )

    elif action == "ask_more":
        state["mode"] = "qa"
        state["ui_state"] = "QA"

        await state_manager.update_state(user_id, **state)

        await query.message.reply_text(
            "❓ Напишите вопрос:",
            reply_markup=get_qa_keyboard()
        )

    elif action == "analysis_history":
        history = await get_user_analysis(user_id)

        if not history:
            await query.message.reply_text(
                "❌ История анализов пуста",
                reply_markup=get_history_back_keyboard()
            )
            return

        await query.message.reply_text(
            "📊 История анализов:",
            reply_markup=get_analysis_history_keyboard(history)
        )

    elif action == "qa_history":
        history = await get_user_qa(user_id)

        if not history:
            await query.message.reply_text(
                "❌ История вопросов пуста",
                reply_markup=get_history_back_keyboard()
            )
            return

        text = "📜 История вопросов:\n\n"

        for item in history[-5:]:
            text += f"❓ {item['question']}\n{item['answer']}\n\n"

        await query.message.reply_text(
            text,
            reply_markup=get_history_back_keyboard()
        )

    elif action == "clear_all":
        await hide_all_analysis(user_id)
        await hide_all_qa(user_id)

        state["current_text_id"] = None
        state["last_result_full"] = None
        state["last_result_short"] = None
        state["last_result_id"] = None
        state["mode"] = "analysis"
        state["ui_state"] = "EMPTY"
        state["params"] = {}

        await state_manager.update_state(user_id, **state)

        await query.message.reply_text(
            "🧹 История очищена\n\n📂 Загрузите новый текст",
            reply_markup=get_empty_keyboard()
        )

    elif action == "short_result":
        short_text = state.get("last_result_short")

        if not short_text:
            await query.message.reply_text("❌ Нет результата")
            return

        title = get_mode_title(state.get("mode"))

        await query.message.reply_text(
            f"{title}\n\n{short_text}",
            reply_markup=get_result_keyboard(
                "short",
                True,
                state.get("mode")
            ),
        )

    elif action == "full_result":
        full_text = state.get("last_result_full")

        if not full_text:
            await query.message.reply_text("❌ Нет результата")
            return

        title = get_mode_title(state.get("mode"))

        await query.message.reply_text(
            f"{title}\n\n{full_text}",
            reply_markup=get_result_keyboard(
                "full",
                True,
                state.get("mode")
            ),
        )

async def handle_analysis_item(query, context, user_id, state, payload):
    item_id = payload[0]

    item = await get_analysis_by_id_for_user(user_id, item_id)

    if not item:
        await query.message.reply_text(
            "❌ Анализ не найден",
            reply_markup=get_back_keyboard()
        )
        return

    title = get_mode_title(item["mode"])

    await query.message.reply_text(
        f"{title}\n\n{item['result']}",
        reply_markup=get_history_back_keyboard()
    )

async def show_menu(query, state):
    ui = state.get("ui_state") or resolve_ui_state(state)

    if ui == "EMPTY":
        await query.message.reply_text(
            "📂 Отправьте текст",
            reply_markup=get_empty_keyboard()
        )

    elif ui == "TEXT_LOADED":
        await query.message.reply_text(
            "🧠 Что вы хотите узнать из текста?",
            reply_markup=get_modes_keyboard()
        )

    elif ui == "RESULT":
        await query.message.reply_text(
            "📊 Выберите действие:",
            reply_markup=get_result_keyboard("short", state.get("is_truncated"), mode=state.get("mode"))
        )

    elif ui == "QA":
        await query.message.reply_text(
            "❓ Задайте вопрос:",
            reply_markup=get_qa_keyboard()
        )

ACTION_MAP = {
    "go": handle_go,
    "mode": handle_mode,
    "param": handle_param,
    "action": handle_action,
    "analysis_item": handle_analysis_item
}