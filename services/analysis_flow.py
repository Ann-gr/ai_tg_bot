from services.analysis_service import run_analysis

async def process_user_input(user_id, state, text=None):
    """
    Единая точка обработки любого ввода пользователя
    """

    mode = state.get("mode")

    # Если пришёл новый текст → сохраняем
    if text and mode != "qa":
        state["last_text"] = text
        return {
            "action": "ask_mode",
            "state": state
        }

    # QA режим (вопрос по тексту)
    if mode == "qa":
        if text:
            state["question"] = text

        if not state.get("last_text"):
            return {"error": "Сначала отправьте текст"}

        if not state.get("question"):
            return {"action": "ask_question"}

        result = await run_analysis(user_id, state["last_text"], state)

        return {
            "action": "show_result",
            "result": result,
            "state": state
        }

    # Обычный анализ
    if not state.get("last_text"):
        return {"error": "Сначала отправьте текст"}

    result = await run_analysis(user_id, state["last_text"], state)

    return {
        "action": "show_result",
        "result": result,
        "state": state
    }