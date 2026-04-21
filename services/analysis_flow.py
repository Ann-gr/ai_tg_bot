from services.text_repository import get_text, save_text
from services.chunk_repository import get_chunks, save_chunks
from utils.relevance import get_top_chunks
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

    context = "\n\n".join(context_chunks)[:1000]

    return {
        "action": "ready_to_stream",
        "text": context,
        "question": question,
    }

async def prepare_analysis_data(user_id, state, new_text=None, user_question=None):
    if state.get("mode") == "qa":
        if not user_question:
            return {"error": "❓ Введите вопрос"}

        return await prepare_qa_context(state, user_question)
    
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

    # достаём текст
    text = await get_text(state["current_text_id"])

    return {
        "action": "ready_to_stream",
        "text": text
    }