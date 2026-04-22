import time

from services.analysis_service import run_analysis_stream
from utils.render import render_result
from state import state_manager

UPDATE_INTERVAL = 0.4
MIN_CHARS = 40

async def stream_and_render(
    edit_func,
    user_id,
    state,
    text,
    question=None,
):
    buffer = ""
    full_text = ""
    last_update = time.time()

    async for chunk in run_analysis_stream(
        text=text,
        state=state,
        user_question=question,
    ):
        buffer += chunk
        full_text += chunk

        now = time.time()

        if len(buffer) >= MIN_CHARS or (now - last_update) > UPDATE_INTERVAL:
            try:
                await edit_func(full_text + "▌")
            except Exception:
                pass

            buffer = ""
            last_update = now

    # финал
    state["last_result"] = full_text
    state["result_view"] = "short"
    state["ui_state"] = "RESULT"

    await state_manager.update_state(user_id, **state)

    await render_result(
        edit_func,
        state,
        full_text
    )

    return full_text