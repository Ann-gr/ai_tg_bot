from services.text_repository import save_text, save_chunks, get_chunks
from services.streaming_service import stream_and_render
from state import state_manager
from handlers.keyboards import get_modes_keyboard
from utils.relevance import select_relevant_chunks
from utils.text_splitter import split_text

async def prepare_analysis_data(user_id, state, new_text=None, user_question=None):
    MAX_CONTEXT_CHARS = 3000
    DEFAULT_TOP_K = 3

    mode = state.get("mode")

    # Новый текст
    if new_text:
        text_id = await save_text(user_id, new_text)
        state["current_text_id"] = text_id

        chunks = split_text(new_text)
        await save_chunks(text_id, chunks)

        return {"action": "ask_mode"}

    # нет текста
    if not state.get("current_text_id"):
        return {"error": "❌ Сначала загрузите текст"}
    
    chunks = await get_chunks(state["current_text_id"])

    # QA режим
    if mode == "qa":
        if not user_question:
            return {"error": "❓ Введите вопрос"}

        selected_chunks = select_relevant_chunks(
            chunks,
            user_question,
            top_k=DEFAULT_TOP_K
        )
    else:
        selected_chunks = chunks[:DEFAULT_TOP_K]

    # Обычный анализ    
    text = "\n\n".join(selected_chunks)

    if len(text) > MAX_CONTEXT_CHARS:
        text = text[:MAX_CONTEXT_CHARS]

    return {
        "action": "ready_to_stream",
        "text": text,
        "question": user_question if mode == "qa" else None
    }

async def run_analysis_pipeline(
    send_func,
    user_id,
    state,
    new_text=None,
    user_question=None,
):
    data = await prepare_analysis_data(
        user_id,
        state,
        new_text=new_text,
        user_question=user_question
    )

    # ошибка
    if data.get("error"):
        await send_func(data["error"])
        return

    # текст загружен → выбор режима
    if data.get("action") == "ask_mode":
        state["ui_state"] = "TEXT_LOADED"
        await state_manager.update_state(user_id, **state)

        await send_func(
            "✅ Текст загружен\n\nВыберите режим:",
            reply_markup=get_modes_keyboard(),
        )
        return

    # стриминг
    await stream_and_render(
        send_func=send_func,
        user_id=user_id,
        state=state,
        text=data.get("text"),
        question=data.get("question"),
    )