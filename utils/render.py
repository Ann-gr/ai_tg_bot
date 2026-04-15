from handlers.keyboards import get_result_keyboard
from utils.mode_utils import get_mode_title
from utils.text_utils import shorten_text


async def render_result(
    send_func,   # функция отправки (edit_text или reply_text)
    state,
    result
):
    """
    Универсальный рендер результата
    """

    title = get_mode_title(state.get("mode"))

    short_text, is_truncated = shorten_text(result)

    text = f"{title}\n\n{short_text}"

    if is_truncated:
        text += "\n\n👇 Нажмите, чтобы посмотреть полностью"

    await send_func(
        text,
        reply_markup=get_result_keyboard(
            state.get("result_view", "short"),
            is_truncated
        )
    )