# AI pipeline
from core.prompt_builder import create_prompt
from services.ai_service import analyze_with_ai
# форматирование ответа
from utils.formatter import format_response
# добавляем историю
from state.user_state import get_history, add_message

async def run_analysis(user_id, text, state):
    mode = state.get("mode", "analysis")

    prompt = create_prompt(
        text,
        mode,
        top_n=state.get("top_n", 10),
        freq_n=state.get("freq_n", 10)
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
    if is_real_text(text):
        add_message(user_id, "user", text)
        add_message(user_id, "assistant", ai_result)

    return format_response(ai_result, mode)