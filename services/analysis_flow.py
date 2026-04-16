from services.analysis_service import run_analysis
from services.text_repository import get_text, save_text
from services.analysis_repository import save_analysis
from services.qa_repository import save_qa
from services.chunk_repository import get_chunks
from state import state_manager
from utils.relevance import get_relevant_chunks, get_top_chunks

async def handle_qa(user_id, state, question):
    if not state.get("current_text_id"):
        return {"error": "Сначала отправьте текст"}

    text_id = state["current_text_id"]

    # получаем чанки
    chunks = await get_chunks(text_id)

    # находим релевантные
    top_chunks = get_top_chunks(chunks, question)

    if not top_chunks:
        context_text = chunks[:2]  # fallback
    else:
        context_text = top_chunks

    context = "\n\n".join(context_text)

    # короткая история
    history = state.get("qa_history", [])[-2:]

    result = await run_analysis(
        user_id,
        context,
        state,
        user_question=question,
        qa_history=history
    )

    # охраняем
    qa_history = state.get("qa_history", [])
    qa_history.append({
        "question": question,
        "answer": result
    })

    state["qa_history"] = qa_history[-5:]

    await save_qa(user_id, text_id, question, result)
    await state_manager.update_state(user_id, **state)

    return {
        "action": "show_result",
        "result": result,
        "state": state
    }

async def process_user_input(user_id, state, new_text=None, user_question=None):
    if state.get("mode") == "qa":
        if not user_question:
            return {"error": "❓ Введите вопрос"}

        return await handle_qa(user_id, state, user_question)
    
    # если пришёл новый текст
    elif new_text:
        text_id = await save_text(user_id, new_text)

        state["current_text_id"] = text_id

        return {
            "action": "ask_mode",
            "state": state
        }

    # если текста нет
    if not state.get("current_text_id"):
        return {"error": "❌ Сначала отправьте текст"}

    # достаём текст
    text = await get_text(state["current_text_id"])
    
    result = await run_analysis(user_id, text, state)

    analysis_id = await save_analysis(
        user_id,
        state["current_text_id"],
        state["mode"],
        result
    )

    return {
        "action": "show_result",
        "result": result,
        "result_id": analysis_id,
        "state": state
    }