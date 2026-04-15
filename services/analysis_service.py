# AI pipeline
from core.prompt_builder import create_prompt
from services.ai_service import analyze_with_ai
# форматирование ответа
from utils.formatter import format_response

async def run_analysis(user_id, text, state):
    mode = state.get("mode", "analysis")

    params = state.get("params", {})
    n = params.get("n", 10)
    question = state.get("question", None)
    qa_history = state.get("qa_history", [])

    prompt = create_prompt(
        text,
        mode,
        top_n=n,
        freq_n=n,
        question=question,
        qa_history=qa_history
    )

    messages = [
        {"role": "system", "content": "You are a precise text analysis assistant. Always respond in Russian"},
    ]

    # история диалога
    for item in qa_history:
        messages.append({"role": "user", "content": item["q"]})
        messages.append({"role": "assistant", "content": item["a"]})

    # текущий запрос
    messages.append({"role": "user", "content": prompt})

    ai_result = await analyze_with_ai(messages)

    return format_response(ai_result, mode)