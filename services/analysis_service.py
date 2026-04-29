# AI pipeline
from core.prompt_builder import create_prompt, SYSTEM_PROMPT
from services.ai_service import stream_ai_response

async def run_analysis_stream(text, state, user_question=None):
    prompt = create_prompt(
        text=text,
        mode=state.get("mode"),
        top_n=state.get("params", {}).get("n", 10),
        question=user_question,
        qa_history=state.get("qa_history", []),
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    for m in messages:
        if len(m["content"]) > 2000:
            m["content"] = m["content"][:2000]

    async for chunk in stream_ai_response(messages):
        yield chunk