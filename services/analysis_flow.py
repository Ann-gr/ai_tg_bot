from services.text_repository import save_text, save_chunks, get_chunks
from services.streaming_service import stream_and_render
from utils.relevance import select_relevant_chunks
from utils.text_splitter import split_text
from handlers.keyboards import get_modes_keyboard
from state import state_manager

async def prepare_qa_context(state, question):
    if not state.get("current_text_id"):
        return {"error": "❌ Сначала загрузите текст (отправьте файл или текст)"}

    text_id = state["current_text_id"]

    # получаем чанки
    chunks = await get_chunks(text_id)
    # находим релевантные
    top_chunks = select_relevant_chunks(chunks, question)

    context_chunks = top_chunks if top_chunks else chunks[:2]

    MAX_CONTEXT_CHARS = 1200

    context = "\n\n".join(context_chunks)

    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS]

    return {
        "action": "ready_to_stream",
        "text": context,
        "question": question,
    }

async def prepare_analysis_data(user_id, state, new_text=None, user_question=None):
    MAX_CONTEXT_CHARS = 3000
    DEFAULT_TOP_K = 3

    # QA режим
    if user_question:
        if not state.get("current_text_id"):
            return {"error": "❌ Сначала загрузите текст"}

        chunks = await get_chunks(state["current_text_id"])

        selected_chunks = select_relevant_chunks(
            chunks,
            user_question,
            top_k=DEFAULT_TOP_K
        )

        text = "\n\n".join(selected_chunks)

        if len(text) > MAX_CONTEXT_CHARS:
            text = text[:MAX_CONTEXT_CHARS]

        return {
            "action": "ready_to_stream",
            "text": text,
            "question": user_question
        }

    # Новый текст
    if new_text:
        text_id = await save_text(user_id, new_text)
        state["current_text_id"] = text_id

        chunks = split_text(new_text)
        await save_chunks(text_id, chunks)

        return {"action": "ask_mode"}

    # Нет текста
    if not state.get("current_text_id"):
        return {"error": "❌ Сначала загрузите текст"}

    # Обычный анализ
    chunks = await get_chunks(state["current_text_id"])
    selected_chunks = chunks[:DEFAULT_TOP_K]

    text = "\n\n".join(selected_chunks)

    if len(text) > MAX_CONTEXT_CHARS:
        text = text[:MAX_CONTEXT_CHARS]

    return {
        "action": "ready_to_stream",
        "text": text
    }

async def run_analysis_pipeline(
    edit_func,
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
        await edit_func(data["error"])
        return None

    # текст загружен → показать выбор режима
    if data.get("action") == "ask_mode":
        state["ui_state"] = "TEXT_LOADED"
        await state_manager.update_state(user_id, **state)

        await edit_func(
            "✅ Текст загружен\n\nВыберите режим:",
            reply_markup=get_modes_keyboard(),
        )
        return None

    # стриминг
    result = await stream_and_render(
        edit_func=edit_func,
        user_id=user_id,
        state=state,
        text=data.get("text"),
        question=data.get("question"),
    )

    return result