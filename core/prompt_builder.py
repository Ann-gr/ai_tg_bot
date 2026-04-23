from core.modes import MODE_REGISTRY

SYSTEM_PROMPT = "You are a professional text analysis assistant. Answer clearly and structured."
MAX_TEXT_LENGTH = 1000
MAX_HISTORY_ITEMS = 1
MAX_Q_LEN = 100
MAX_A_LEN = 200

def trim_text(text: str) -> str:
    if len(text) <= MAX_TEXT_LENGTH:
        return text
    return text[:MAX_TEXT_LENGTH]

def build_qa_history(history: list) -> str:
    if not history:
        return ""

    short_history = ""

    for item in history[-MAX_HISTORY_ITEMS:]:
        q = item.get("Вопрос", "")[:MAX_Q_LEN]
        a = item.get("Ответ", "")[:MAX_A_LEN]

        short_history += f"\nВопрос: {q}\nОтвет: {a}\n"

    return short_history


def create_prompt(text: str, mode: str = "analysis", **kwargs) -> str:
    config = MODE_REGISTRY.get(mode, MODE_REGISTRY["analysis"])
    mode_prompt = config["prompt"]

    # параметры
    top_n = kwargs.get("top_n", 10)
    question = kwargs.get("question")
    qa_history = kwargs.get("qa_history", [])

    # форматируем mode prompt
    try:
        mode_prompt = mode_prompt.format(
            top_n=top_n,
            question=question or ""
        )
    except KeyError:
        pass  # если режим без параметров

    # --- QA режим ---
    if mode == "qa":
        history_block = build_qa_history(qa_history)

        return f"""
Context:
{trim_text(text)}

{history_block}

{mode_prompt}
"""

    # --- обычные режимы ---
    return f"""
Text:
{trim_text(text)}

{mode_prompt}
"""