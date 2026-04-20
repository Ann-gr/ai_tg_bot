# AI pipeline
from core.prompt_builder import create_prompt, SYSTEM_PROMPT
from services.ai_service import analyze_with_ai
# форматирование ответа
from utils.formatter import format_response

async def run_analysis(user_id, text, state, user_question=None):
    mode = state.get("mode", "analysis")
    params = state.get("params", {})

    top_n = params.get("n", 10)

    prompt = create_prompt(
        text=text,
        mode=mode,
        top_n=top_n,
        question=user_question,
        qa_history=state.get("qa_history", [])
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    ai_result = await analyze_with_ai(messages)

    return format_response(ai_result, mode)