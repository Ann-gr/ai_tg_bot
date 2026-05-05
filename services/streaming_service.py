import time

from services.analysis_service import run_analysis_stream
from services.history_repository import save_analysis, save_qa
from utils.render import render_result
from utils.text_utils import shorten_text
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
    state["result_view"] = "short"
    state["ui_state"] = "RESULT"

    await state_manager.update_state(user_id, **state)
    
    # пост-обработка (частотный анализ)
    if state.get("mode") == "frequency":
        n = state.get("params", {}).get("n", 10)
        processed_text = trim_frequency_result(full_text, n)
    else:
        processed_text = full_text

    # сохраняем ДВА варианта
    state["last_result_full"] = processed_text
    state["last_result_short"], _ = shorten_text(processed_text)

    state["result_view"] = "short"
    state["ui_state"] = "RESULT"

    await state_manager.update_state(user_id, **state)

    # показываем короткую версию
    await render_result(
        edit_func,
        state,
        state["last_result_short"]
    )

    try:
        if state.get("mode") == "qa":
            await save_qa(
                user_id,
                state.get("current_text_id"),
                question,
                full_text
            )
        else:
            analysis_id = await save_analysis(
                user_id,
                state.get("current_text_id"),
                state.get("mode"),
                full_text
            )

            state["last_result_id"] = analysis_id
            await state_manager.update_state(user_id, **state)

    except Exception as e:
        print("❌ Ошибка сохранения:", e)

    return full_text

def trim_frequency_result(text: str, top_n: int):
    lines = text.split("\n")
    result = []
    
    for line in lines:
        if line.strip().startswith(tuple(str(i) for i in range(1, 100))):
            result.append(line)
    
    return "\n".join(result[:top_n])