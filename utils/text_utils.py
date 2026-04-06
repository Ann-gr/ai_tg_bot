def shorten_text(text: str, max_length: int = 500) -> tuple[str, bool]:
    if len(text) <= max_length:
        return text, False

    short = text[:max_length].rstrip() + "..."
    return short, True