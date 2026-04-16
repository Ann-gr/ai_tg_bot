from core.modes import MODE_REGISTRY, BASE_PROMPT
def create_prompt(text, mode="analysis", **kwargs):
    config = MODE_REGISTRY.get(mode, MODE_REGISTRY["analysis"])

    base_prompt = BASE_PROMPT.format(text=text)
    mode_prompt = config["prompt"].format(**kwargs)

    # QA history (ограниченная)
    if mode == "qa":
        history = kwargs.get("qa_history", [])

        short_history = ""
        for item in history[-3:]:
            short_q = item["q"][:100]
            short_a = item["a"][:200]

            short_history += f"\nВопрос: {short_q}\nОтвет: {short_a}\n"

        if short_history:
            base_prompt += f"\n\nИстория диалога:\n{short_history}"

    return base_prompt + "\n" + mode_prompt