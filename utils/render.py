from handlers.keyboards import get_result_keyboard
from utils.mode_utils import get_mode_title
from utils.text_utils import shorten_text

async def render_result(edit_func, state):
    title = get_mode_title(state.get("mode"))

    if state.get("result_view") == "full":
        text = state.get("last_result_full")
    else:
        text = state.get("last_result_short")

    is_truncated = state.get("is_truncated", False)

    message = f"{title}\n\n{text}"

    if is_truncated and state.get("result_view") == "short":
        message += "\n\n👇 Нажмите, чтобы посмотреть полностью"

    await edit_func(
        message,
        reply_markup=get_result_keyboard(
            state.get("result_view"),
            is_truncated,
            state.get("mode")
        )
    )