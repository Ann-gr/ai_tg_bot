from services.analysis_service import run_analysis
import uuid

async def process_user_input(user_id, state, text=None):
    """
    Единая точка обработки любого ввода пользователя
    """

    mode = state.get("mode")

    # режим QA
    if mode == "qa":
        if text:
            state["question"] = text

        if not state.get("last_text"):
            return {"error": "Сначала отправьте текст"}

        result = await run_analysis(user_id, state["last_text"], state)

        qa_history = state.get("qa_history", [])

        qa_history.append({
            "q": state.get("question"),
            "a": result,
            "visible": True
        })
        
        state["qa_history"] = qa_history[-10:]

        return {
            "action": "show_result",
            "result": result,
            "state": state
        }

    # Если пришёл новый текст (НЕ QA)
    if text:
        state["last_text"] = text
        state["question"] = None  # важно сбрасывать
        return {
            "action": "ask_mode",
            "state": state
        }

    # Обычный анализ
    if not state.get("last_text"):
        return {"error": "Сначала отправьте текст"}

    result = await run_analysis(user_id, state["last_text"], state)

    analysis_history = state.get("analysis_history", [])
    analysis_history.append({
        "id": str(uuid.uuid4()),
        "mode": mode,
        "result": result,
        "visible": True
    })
    state["analysis_history"] = analysis_history[-10:]

    return {
        "action": "show_result",
        "result": result,
        "state": state
    }