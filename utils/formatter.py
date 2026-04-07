def clean_ai_response(text: str) -> str:
    """
    Очищает ответ AI и делает его пригодным для Telegram
    """

    if not text:
        return "⚠️ Не удалось получить ответ от AI"

    # убираем лишние пробелы
    text = text.strip()

    # удаляем возможные ```json ``` или ```
    text = text.replace("```json", "").replace("```", "")

    return text

def limit_length(text: str, max_chars: int = 3500) -> str:
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... (ответ сокращён)"
    return text

def format_response(text: str, mode: str) -> str:
    text = clean_ai_response(text)
    text = limit_length(text)
    return text