from services.text_repository import save_text, save_chunks, get_chunks
from services.streaming_service import stream_and_render
from utils.relevance import get_top_chunks, select_relevant_chunks
from utils.text_splitter import split_text

async def prepare_qa_context(state, question):
    if not state.get("current_text_id"):
        return {"error": "❌ Сначала загрузите текст (отправьте файл или текст)"}

    text_id = state["current_text_id"]

    # получаем чанки
    chunks = await get_chunks(text_id)
    # находим релевантные
    top_chunks = get_top_chunks(chunks, question)

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

    if state.get("mode") == "qa" or user_question:
        if not user_question:
            return {"error": "❓ Введите вопрос"}

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
    
    # если пришёл новый текст
    elif new_text:
        text_id = await save_text(user_id, new_text)
        state["current_text_id"] = text_id

        chunks = split_text(new_text)
        await save_chunks(text_id, chunks)

        return {"action": "ask_mode"}

    # если текста нет
    if not state.get("current_text_id"):
        return {"error": "❌ Сначала загрузите текст (отправьте файл или текст)"}

    # Анализ (не QA)
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
):
    data = await prepare_analysis_data(user_id, state)

    if data.get("error"):
        await edit_func(data["error"])
        return None

    result = await stream_and_render(
        edit_func=edit_func,
        user_id=user_id,
        state=state,
        text=data.get("text"),
        question=data.get("question"),
    )

    return result