from handlers.keyboards import get_result_keyboard
from utils.mode_utils import get_mode_title
from utils.text_utils import shorten_text


async def render_result(edit_func, state, text):
    title = get_mode_title(state.get("mode"))

    short_text, is_truncated = shorten_text(text)

    if state.get("result_view") == "full":
        final_text = text
    else:
        final_text = short_text

    message = f"{title}\n\n{final_text}"

    if is_truncated:
        message += "\n\n👇 Нажмите, чтобы посмотреть полностью"

    await edit_func(
        message,
        reply_markup=get_result_keyboard(state.get("result_view"), is_truncated, state.get("mode"))
    )