from services.analysis_service import run_analysis

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

        if not state.get("question"):
            return {"action": "ask_question", "state": state}

        result = await run_analysis(user_id, state["last_text"], state)

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

    # единая точка сохранения истории вопросов и анализов
    if mode == "qa":
        qa_history = state.get("qa_history", [])
        qa_history.append({
            "q": state.get("question"),
            "a": result
        })
        state["qa_history"] = qa_history[-10:]
    else:
        analysis_history = state.get("analysis_history", [])
        analysis_history.append({
            "mode": mode,
            "result": result
        })
        state["analysis_history"] = analysis_history[-10:]

    return {
        "action": "show_result",
        "result": result,
        "state": state
    }