# AI pipeline
from core.prompt_builder import create_prompt
from services.ai_service import analyze_with_ai
# форматирование ответа
from utils.formatter import format_response
# добавляем историю
from state import state_manager

async def run_analysis(user_id, text, state):
    mode = state.get("mode", "analysis")

    params = state.get("params", {})
    n = params.get("n", 10)

    prompt = create_prompt(
        text,
        mode,
        top_n=n,
        freq_n=n
    )

    messages = [
        {"role": "user", "content": prompt}
    ]

    ai_result = await analyze_with_ai(messages)

    def is_real_text(text):
        CONTROL_WORDS = [
            "📊", "📝", "🔑", "📈", "🆕", "📜", "🧹", "⬅️"
        ]
        return not any(text.startswith(c) for c in CONTROL_WORDS)

    # сохраняем только диалог
    if is_real_text(ai_result):
        state_manager.add_message(user_id, "user", text)
        state_manager.add_message(user_id, "assistant", ai_result)

        state_manager.set_last_text(user_id, text)
        state_manager.set_last_result(user_id, ai_result)
    return format_response(ai_result, mode)